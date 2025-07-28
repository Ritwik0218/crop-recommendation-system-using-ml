#!/usr/bin/env python3
"""
Production monitoring script for Crop Recommendation System.
This script continuously monitors the application health and logs the status.
"""

import requests
import time
import json
import logging
from datetime import datetime
import sys
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class HealthMonitor:
    def __init__(self, base_url="http://localhost:5001", check_interval=30):
        self.base_url = base_url.rstrip('/')
        self.check_interval = check_interval
        self.health_url = f"{self.base_url}/health"
        self.consecutive_failures = 0
        self.max_failures = 3
        
    def check_health(self):
        """Perform health check and return status."""
        try:
            response = requests.get(self.health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Detailed health analysis
                status = data.get('status', 'unknown')
                models_loaded = data.get('models_loaded', False)
                version = data.get('version', 'unknown')
                
                if status == 'healthy' and models_loaded:
                    logger.info(f"✅ Application healthy - Version: {version}")
                    self.consecutive_failures = 0
                    return True, data
                else:
                    logger.warning(f"⚠️  Application unhealthy - Status: {status}, Models: {models_loaded}")
                    self.consecutive_failures += 1
                    return False, data
            else:
                logger.error(f"❌ Health check failed - HTTP {response.status_code}")
                self.consecutive_failures += 1
                return False, {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection failed - Application may be down")
            self.consecutive_failures += 1
            return False, {"error": "Connection failed"}
        except requests.exceptions.Timeout:
            logger.error(f"❌ Health check timeout")
            self.consecutive_failures += 1
            return False, {"error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            self.consecutive_failures += 1
            return False, {"error": str(e)}
    
    def check_endpoints(self):
        """Check additional endpoints for more comprehensive monitoring."""
        endpoints = [
            ('/', 'Main page'),
            ('/favicon.ico', 'Favicon')
        ]
        
        results = {}
        for endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=5)
                results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'description': description
                }
            except Exception as e:
                results[endpoint] = {
                    'error': str(e),
                    'description': description
                }
        
        return results
    
    def test_prediction(self):
        """Test the prediction functionality with sample data."""
        try:
            prediction_data = {
                'Nitrogen': '90',
                'Phosporus': '42',  # Note: keeping original field name
                'Potassium': '43',
                'Temperature': '20.5',
                'Humidity': '82',
                'Ph': '6.5',
                'Rainfall': '202'
            }
            
            response = requests.post(
                f"{self.base_url}/predict",
                data=prediction_data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ Prediction endpoint working")
                return True, {"status": "success", "status_code": 200}
            else:
                logger.warning(f"⚠️  Prediction endpoint returned {response.status_code}")
                return False, {"status": "error", "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"❌ Prediction test failed: {e}")
            return False, {"status": "error", "error": str(e)}
    
    def run_comprehensive_check(self):
        """Run a comprehensive health check including all endpoints."""
        logger.info("🔍 Running comprehensive health check...")
        
        # 1. Basic health check
        health_ok, health_data = self.check_health()
        
        # 2. Endpoint availability
        endpoint_results = self.check_endpoints()
        
        # 3. Prediction functionality
        prediction_ok, prediction_data = self.test_prediction()
        
        # Summary
        overall_status = health_ok and prediction_ok
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if overall_status else 'unhealthy',
            'health_check': health_data,
            'endpoints': endpoint_results,
            'prediction_test': prediction_data,
            'consecutive_failures': self.consecutive_failures
        }
        
        if overall_status:
            logger.info("🎉 Comprehensive health check passed")
        else:
            logger.error("💀 Comprehensive health check failed")
        
        return overall_status, report
    
    def monitor_continuously(self):
        """Run continuous monitoring."""
        logger.info(f"🚀 Starting continuous monitoring of {self.base_url}")
        logger.info(f"⏰ Check interval: {self.check_interval} seconds")
        
        try:
            while True:
                is_healthy, _ = self.check_health()
                
                # Alert on consecutive failures
                if self.consecutive_failures >= self.max_failures:
                    logger.critical(f"🚨 ALERT: {self.consecutive_failures} consecutive failures!")
                
                # Run comprehensive check every 10th iteration
                if time.time() % (self.check_interval * 10) < self.check_interval:
                    self.run_comprehensive_check()
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"💥 Monitoring error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Crop Recommendation System Health Monitor")
    parser.add_argument("--url", default="http://localhost:5001", help="Base URL to monitor")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run check once and exit")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive check")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(base_url=args.url, check_interval=args.interval)
    
    if args.once:
        if args.comprehensive:
            is_healthy, report = monitor.run_comprehensive_check()
            print(json.dumps(report, indent=2))
        else:
            is_healthy, data = monitor.check_health()
            print(json.dumps(data, indent=2))
        sys.exit(0 if is_healthy else 1)
    else:
        monitor.monitor_continuously()

if __name__ == "__main__":
    main()
