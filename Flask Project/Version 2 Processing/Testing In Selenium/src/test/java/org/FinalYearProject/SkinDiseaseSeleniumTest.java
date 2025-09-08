package org.FinalYearProject;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.edge.EdgeDriver;
import io.github.bonigarcia.wdm.WebDriverManager;

public class SkinDiseaseSeleniumTest {

    private WebDriver driver;

    // Setup method: prepares EdgeDriver
    public void setup() {
        // Automatically download & setup EdgeDriver
        WebDriverManager.edgedriver().setup();

        // Initialize Edge browser
        driver = new EdgeDriver();

        // Maximize browser window
        driver.manage().window().maximize();
    }

    // Example test method
    public void testWebsite() {
        // Open your web app or any test URL
        driver.get("https://www.example.com");

        // Add your Selenium steps here
        // Example: driver.findElement(By.id("someId")).click();
        System.out.println("Page title is: " + driver.getTitle());
    }

    // Teardown method: closes the browser
    public void teardown() {
        if (driver != null) {
            driver.quit();
        }
    }

    // Main method to run the test
    public static void main(String[] args) {
        SkinDiseaseSeleniumTest test = new SkinDiseaseSeleniumTest();
        test.setup();
        test.testWebsite();
        test.teardown();
    }
}
