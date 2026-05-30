# Bincom Python Developer Intern Assessment

This is a lightweight Python web application built with Flask to display, aggregate, and store election polling unit results. It was developed as part of the Bincom Tech Internship Programme assessment.

## Features
* **Individual Polling Unit Results:** View the scores for all parties at any specific polling unit.
* **Aggregated LGA Results:** Dynamically calculates and displays the summed total results of all polling units under a selected Local Government Area (LGA) using SQL `JOIN` queries.
* **Store New Results:** A user-friendly data entry form featuring an asynchronous, chained dropdown API (State -> LGA -> Ward -> Polling Unit) to securely insert new party scores into the database.

## Tech Stack
* **Backend:** Python, Flask
* **Database:** MySQL (using `mysql-connector-python`)
* **Frontend:** HTML5, vanilla JavaScript (Fetch API for dynamic UI)

## Prerequisites
To run this application locally, you will need:
* Python 3.x installed
* A local MySQL server (like XAMPP or WAMP)

## Local Setup & Installation

**1. Database Initialization**
* Start your local MySQL server (e.g., via XAMPP Control Panel).
* Open phpMyAdmin (`http://localhost/phpmyadmin`).
* Create a new database named exactly `bincomphptest`.
* Import the provided `bincom_test.sql` file into this new database.

**2. Application Setup**
* Clone this repository or download the project folder.
* Open your terminal and navigate to the project directory.
* Install the required Python dependencies:
  ```bash
  pip install Flask mysql-connector-python
  
  ```
  
**3. Run the Server**
* Execute the main Python file:
 ```bash
 python app.py
 ```
 * Open your web browser and navigate to http://127.0.0.1:5000 to view the application
 
 
Author
``` Martin Diarua ```