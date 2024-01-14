import subprocess

class ZaraMonitor():
    def __init__(self, url):
        self.is_found = False
        self.monitor_url = url

    def run_playwright_test(self, test_name):
    # Construct the command to run the Playwright test
        command = f'npx playwright test {test_name} --headed'

        try:
        # Run the command and capture the output
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        # Check the result and return True if the test passed, False otherwise
            if result.returncode == 0:
               return True
            else:
                return False

        except subprocess.CalledProcessError as e:
            return False  
    

    def check(self):
        print('Checking {}'.format(self.monitor_url))
        return self.run_playwright_test(self.monitor_url)

    


