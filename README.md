# Andhra Cuisine by Tigers Truck

## Project Overview
This project is a full-stack web application for "Andhra Cuisine by Tigers Truck," designed to provide a seamless experience for customers to browse the menu, place orders, make payments, and submit reviews. The application is built using Python Flask for the backend and utilizes MySQL as the database, with a focus on a high-quality user interface.

## Features
- User authentication (registration and login)
- Browse and order from a dynamic menu
- View and manage cart items
- Checkout process with order summary
- Submit reviews for dishes
- User dashboard to view past orders and reviews

## Project Structure
```
andhra-cuisine-app
├── app.py                     # Main application file
├── requirements.txt           # Python dependencies
├── database_schema.sql        # SQL commands for database schema
├── static                     # Static files (CSS, JS, images)
│   ├── css
│   │   ├── main.css           # Main CSS styles
│   │   └── style.css          # Additional CSS styles
│   ├── js
│   │   └── main.js            # JavaScript for client-side functionality
│   └── images
│       └── logo.png           # Logo image
├── templates                  # HTML templates for rendering views
│   ├── index.html             # Main landing page
│   ├── menu.html              # Menu items page
│   ├── order.html             # Cart page
│   ├── bill.html              # Order summary page
│   ├── dashboard.html          # User dashboard
│   ├── login.html             # Login form
│   ├── register.html          # Registration form
│   └── checkout.html          # Checkout page
├── venv                       # Virtual environment
└── README.md                  # Project documentation
```

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd andhra-cuisine-app
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   - Use XAMPP to start the MySQL server.
   - Open a MySQL client and run the commands in `database_schema.sql` to create the necessary tables.

6. **Run the application**:
   ```
   python app.py
   ```
   Access the application in your web browser at `http://127.0.0.1:5000`.

## Usage
- Register a new account or log in to an existing account.
- Browse the menu and add items to your cart.
- Proceed to checkout to place your order.
- View your order summary and submit reviews for your favorite dishes.

## License
This project is licensed under the MIT License.