#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for SmartQuote RFP Orchestrator
Tests all auth, RFP, pipeline, approval, client portal, and utility endpoints
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class SmartQuoteAPITester:
    def __init__(self, base_url: str = "https://smartquote-engine.preview.emergentagent.com"):
        self.base_url = base_url
        self.tokens = {}  # Store tokens for different users
        self.test_data = {}  # Store test data like RFP IDs
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        if details:
            print(f"    {details}")
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append(f"{name}: {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    token: Optional[str] = None, expected_status: int = 200) -> tuple[bool, Dict]:
        """Make HTTP request and validate response"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}

            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    # ==================== AUTH TESTS ====================
    def test_auth_endpoints(self):
        """Test all authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test credentials from test_credentials.md
        test_accounts = [
            {"email": "admin@smartquote.in", "password": "Admin@123", "role": "admin"},
            {"email": "owner@smartquote.in", "password": "Owner@123", "role": "owner"},
            {"email": "sales@smartquote.in", "password": "Sales@123", "role": "sales"},
            {"email": "client@pmc.gov.in", "password": "Client@123", "role": "client"},
        ]

        for account in test_accounts:
            # Test login
            success, response = self.make_request(
                "POST", "auth/login", 
                {"email": account["email"], "password": account["password"]}
            )
            
            if success and "token" in response:
                self.tokens[account["role"]] = response["token"]
                self.log_test(f"Login {account['role']}", True, f"Token received for {account['email']}")
                
                # Test /auth/me with token
                me_success, me_response = self.make_request("GET", "auth/me", token=response["token"])
                if me_success and me_response.get("role") == account["role"]:
                    self.log_test(f"Auth/me {account['role']}", True, f"Role verified: {me_response.get('role')}")
                else:
                    self.log_test(f"Auth/me {account['role']}", False, f"Role mismatch or error: {me_response}")
            else:
                self.log_test(f"Login {account['role']}", False, f"Login failed: {response}")

        # Test registration
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@test.com"
        reg_success, reg_response = self.make_request(
            "POST", "auth/register",
            {
                "email": test_email,
                "password": "Test@123",
                "name": "Test User",
                "role": "client",
                "company_name": "Test Company"
            }
        )
        self.log_test("Registration", reg_success, f"New user: {test_email}")

    # ==================== RFP TESTS ====================
    def test_rfp_endpoints(self):
        """Test RFP submission and listing"""
        print("\n📄 Testing RFP Endpoints...")
        
        if "client" not in self.tokens:
            self.log_test("RFP Submit", False, "No client token available")
            return

        # Test RFP submission
        rfp_data = {
            "title": "Test RFP - LED Street Lights",
            "raw_text": "We need 100 LED street lights, 150W each, IP65 rated, for municipal installation. Delivery within 30 days. Please provide quotation with GST.",
            "client_name": "Test Municipality",
            "client_state": "Maharashtra",
            "currency": "INR",
            "tax_type": "intra_state"
        }

        submit_success, submit_response = self.make_request(
            "POST", "rfp/submit", rfp_data, token=self.tokens["client"]
        )
        
        if submit_success and "rfp_id" in submit_response:
            rfp_id = submit_response["rfp_id"]
            self.test_data["rfp_id"] = rfp_id
            self.log_test("RFP Submit", True, f"RFP ID: {rfp_id}")
            
            # Test RFP list
            list_success, list_response = self.make_request("GET", "rfp/list", token=self.tokens["client"])
            if list_success and isinstance(list_response, list):
                self.log_test("RFP List", True, f"Found {len(list_response)} RFPs")
            else:
                self.log_test("RFP List", False, f"List error: {list_response}")
                
            # Test get specific RFP
            get_success, get_response = self.make_request("GET", f"rfp/{rfp_id}", token=self.tokens["client"])
            if get_success and get_response.get("rfp_id") == rfp_id:
                self.log_test("RFP Get", True, f"Retrieved RFP: {get_response.get('title')}")
            else:
                self.log_test("RFP Get", False, f"Get error: {get_response}")
        else:
            self.log_test("RFP Submit", False, f"Submit failed: {submit_response}")

    # ==================== PIPELINE TESTS ====================
    def test_pipeline_execution(self):
        """Test the multi-agent pipeline execution"""
        print("\n🤖 Testing Pipeline Execution...")
        
        if "owner" not in self.tokens or "rfp_id" not in self.test_data:
            self.log_test("Pipeline Run", False, "Missing owner token or RFP ID")
            return

        rfp_id = self.test_data["rfp_id"]
        
        # Run pipeline
        pipeline_success, pipeline_response = self.make_request(
            "POST", f"rfp/{rfp_id}/run-pipeline", token=self.tokens["owner"]
        )
        
        if pipeline_success:
            self.log_test("Pipeline Run", True, 
                f"Status: {pipeline_response.get('status')}, "
                f"Items: {pipeline_response.get('items_priced')}, "
                f"Strategy: {pipeline_response.get('strategy')}")
            
            # Verify RFP was updated with pipeline results
            get_success, get_response = self.make_request("GET", f"rfp/{rfp_id}", token=self.tokens["owner"])
            if get_success and get_response.get("pipeline_result"):
                pipeline_result = get_response["pipeline_result"]
                
                # Check if all pipeline components are present
                components = ["parsed", "pricing", "competitor_analysis", "governance"]
                missing = [c for c in components if c not in pipeline_result]
                
                if not missing:
                    self.log_test("Pipeline Components", True, "All agents completed successfully")
                    
                    # Store pipeline data for further tests
                    self.test_data["pipeline_result"] = pipeline_result
                    
                    # Check pricing details
                    pricing = pipeline_result.get("pricing", {})
                    if pricing.get("summary", {}).get("grand_total", 0) > 0:
                        self.log_test("Pricing Engine", True, f"Total: Rs {pricing['summary']['grand_total']:,.0f}")
                    else:
                        self.log_test("Pricing Engine", False, "No pricing calculated")
                        
                    # Check competitor analysis
                    comp_analysis = pipeline_result.get("competitor_analysis", {})
                    if comp_analysis.get("overall_strategy"):
                        self.log_test("Competitor Analysis", True, f"Strategy: {comp_analysis['overall_strategy']}")
                    else:
                        self.log_test("Competitor Analysis", False, "No strategy determined")
                        
                    # Check governance
                    governance = pipeline_result.get("governance", {})
                    if "requires_approval" in governance:
                        self.log_test("Governance Check", True, f"Approval required: {governance['requires_approval']}")
                    else:
                        self.log_test("Governance Check", False, "No governance result")
                        
                else:
                    self.log_test("Pipeline Components", False, f"Missing: {missing}")
            else:
                self.log_test("Pipeline Results", False, "No pipeline result in RFP")
        else:
            self.log_test("Pipeline Run", False, f"Pipeline failed: {pipeline_response}")

    # ==================== APPROVAL TESTS ====================
    def test_approval_workflow(self):
        """Test approval workflow"""
        print("\n✅ Testing Approval Workflow...")
        
        if "owner" not in self.tokens or "rfp_id" not in self.test_data:
            self.log_test("Approval", False, "Missing owner token or RFP ID")
            return

        rfp_id = self.test_data["rfp_id"]
        
        # Test approval
        approval_success, approval_response = self.make_request(
            "POST", f"rfp/{rfp_id}/approve",
            {"action": "approve", "comments": "Approved for testing"},
            token=self.tokens["owner"]
        )
        
        if approval_success:
            self.log_test("Approval", True, f"Status: {approval_response.get('status')}")
            
            # Test sharing with client
            share_success, share_response = self.make_request(
                "POST", f"rfp/{rfp_id}/share", token=self.tokens["owner"]
            )
            
            if share_success and "share_token" in share_response:
                self.test_data["share_token"] = share_response["share_token"]
                self.log_test("Share with Client", True, f"Token: {share_response['share_token'][:10]}...")
            else:
                self.log_test("Share with Client", False, f"Share failed: {share_response}")
        else:
            self.log_test("Approval", False, f"Approval failed: {approval_response}")

    # ==================== CLIENT PORTAL TESTS ====================
    def test_client_portal(self):
        """Test client portal endpoints"""
        print("\n👥 Testing Client Portal...")
        
        if "client" not in self.tokens or "rfp_id" not in self.test_data:
            self.log_test("Client Quote View", False, "Missing client token or RFP ID")
            return

        rfp_id = self.test_data["rfp_id"]
        
        # Test client quote view
        quote_success, quote_response = self.make_request(
            "GET", f"client/quote/{rfp_id}", token=self.tokens["client"]
        )
        
        if quote_success:
            self.log_test("Client Quote View", True, 
                f"Quote: {quote_response.get('quote_number')}, "
                f"Total: Rs {quote_response.get('grand_total', 0):,.0f}")
            
            # Test client action
            action_success, action_response = self.make_request(
                "POST", f"client/quote/{rfp_id}/action",
                {"action": "approve", "comments": "Looks good, approved!"},
                token=self.tokens["client"]
            )
            
            if action_success:
                self.log_test("Client Action", True, f"Status: {action_response.get('status')}")
            else:
                self.log_test("Client Action", False, f"Action failed: {action_response}")
        else:
            self.log_test("Client Quote View", False, f"Quote view failed: {quote_response}")

    # ==================== PDF TESTS ====================
    def test_pdf_generation(self):
        """Test PDF generation"""
        print("\n📄 Testing PDF Generation...")
        
        if "owner" not in self.tokens or "rfp_id" not in self.test_data:
            self.log_test("PDF Generation", False, "Missing owner token or RFP ID")
            return

        rfp_id = self.test_data["rfp_id"]
        
        # Test PDF generation (we'll check if endpoint responds, not download full PDF)
        try:
            url = f"{self.base_url}/api/rfp/{rfp_id}/pdf"
            headers = {'Authorization': f'Bearer {self.tokens["owner"]}'}
            response = requests.head(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.log_test("PDF Generation", True, f"PDF endpoint accessible")
            else:
                self.log_test("PDF Generation", False, f"PDF endpoint returned {response.status_code}")
        except Exception as e:
            self.log_test("PDF Generation", False, f"PDF request failed: {e}")

    # ==================== UTILITY TESTS ====================
    def test_utility_endpoints(self):
        """Test utility endpoints like SKUs, samples, dashboard"""
        print("\n🛠️ Testing Utility Endpoints...")
        
        if "owner" not in self.tokens:
            self.log_test("Utility Endpoints", False, "Missing owner token")
            return

        # Test SKU catalog
        sku_success, sku_response = self.make_request("GET", "skus", token=self.tokens["owner"])
        if sku_success and isinstance(sku_response, list):
            self.log_test("SKU Catalog", True, f"Found {len(sku_response)} SKUs")
        else:
            self.log_test("SKU Catalog", False, f"SKU error: {sku_response}")

        # Test sample RFPs
        sample_success, sample_response = self.make_request("GET", "sample-rfps", token=self.tokens["owner"])
        if sample_success and isinstance(sample_response, list):
            self.log_test("Sample RFPs", True, f"Found {len(sample_response)} samples")
        else:
            self.log_test("Sample RFPs", False, f"Sample error: {sample_response}")

        # Test dashboard KPIs
        kpi_success, kpi_response = self.make_request("GET", "dashboard/kpis", token=self.tokens["owner"])
        if kpi_success and "total_rfps" in kpi_response:
            self.log_test("Dashboard KPIs", True, f"Total RFPs: {kpi_response['total_rfps']}")
        else:
            self.log_test("Dashboard KPIs", False, f"KPI error: {kpi_response}")

        # Test audit trail
        if "rfp_id" in self.test_data:
            audit_success, audit_response = self.make_request(
                "GET", f"rfp/{self.test_data['rfp_id']}/audit", token=self.tokens["owner"]
            )
            if audit_success and isinstance(audit_response, list):
                self.log_test("Audit Trail", True, f"Found {len(audit_response)} events")
            else:
                self.log_test("Audit Trail", False, f"Audit error: {audit_response}")

    # ==================== MAIN TEST RUNNER ====================
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting SmartQuote API Testing...")
        print(f"Backend URL: {self.base_url}")
        
        # Run test suites in order
        self.test_auth_endpoints()
        self.test_rfp_endpoints()
        self.test_pipeline_execution()
        self.test_approval_workflow()
        self.test_client_portal()
        self.test_pdf_generation()
        self.test_utility_endpoints()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"  - {failure}")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = SmartQuoteAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)