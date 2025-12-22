# Eventhub💙

Eventhub is a simple, responsive and user-friendly platform that makes buying and selling tickets for events easier than ever.

<p align="center">
  <img src="https://github.com/user-attachments/assets/7de8852e-a1f4-4784-9f31-cc99c09fd788" alt="Eventhub Readme Preview">
</p>

## **Why Eventhub? 🏆**

Eventhub was created to solve common frustrations with traditional ticketing platforms such as complicated interfaces, outdated designs and poor user experience. The mission was to create an intuitive, easy-to-use platform, that yet has a variety of different features that users need.

**The goal:** Make it easy for anyone to become an event organizer or attendee, without complications on either side. The platform is designed to put users first, no matter whether you’re managing an event or looking to buy tickets for your next adventure.

With scalability in mind, Eventhub is designed to grow and adapt to future needs, making it easy to add new features. At the same time, security and efficiency remain at the core of the platform.


## **Key Features:**

### **User-Friendly Interface**

* 🌟 **Landing Page**: Eye-catching intro to Eventhub.
* 🔑 **Login & Register**: Simple email/password authentication.
* 🧑‍💻 **Account Page**: Manage your profile, password, Stripe account, view events you've created and orders you've made.

### **Discover Events with Ease**
* 🔥 **Personalized Recommendations**: Get event recommendations based on where you are and your purchase history.
* 🔍 **Event Search & Filters**: Search by location, date, price, category and more.
* 📅 **Upcoming Events**: View all the events you've purchased tickets for.

### **Create & Manage Your Events**

* 📝 **Create Event**: Intuitive form to create new events with image uploads, descriptions and pricing zones.
* 🎉 **Your Events**: View and manage the events you've created.
* 🎫 **Ticket Validation**: Validate tickets for the event and allow others to help with validation.
* 💾 **Export Data**: In case manual validation is preferred, download a CSV with all ticket purchases.

### **Buy Tickets**

* 🎤 **Event Page**: Get all the information you need about an event.
* 💳 **Checkout Page**: Fast and secure checkout powered with Stripe.
* ✅ **Purchase Confirmation**: Get an immediate confirmation after ticket purchase.
* 🧾 **Download Receipts**: Be able to always download a receipt for the purchase.

### **Responsiveness**

* 📱 **Responsive Design**: The platform works seamlessly across all devices.
* 🌙 **Dark/Light Theme**: Switch between dark and light themes to suit preferences.
* 🎬 **Micro-Interactions**: Hover effects, animations and easy-to-navigate design.

### **Developer-Friendly**

* ⚙️ **Comprehensive Documentation**: Clear documentation for easy maintenance and updates.


## **How Eventhub Was Built 🔧**

Eventhub was built to be easy to use, scalable and secure. Django, in combination with PostgreSQL, was chosen for its flexibility and speed, allowing the platform to grow with increasing amount of users, events and purchases. For the frontend, HTML, CSS and JavaScript were used to ensure smooth experience across all devices.

For secure and reliable payments, Stripe is integrated as the payment processor. With Stripe's robust security features, user data is protected and payments are processed smoothly.

### **Technologies Used**

* **Frontend**: Built using HTML, CSS and JavaScript to create a responsive and user-friendly interface.
* **Backend**: Python (Django) was used for a stable and scalable backend-side architecture.
* **Database**: PostgreSQL helps store user data, event info and ticket purchases.
* **Payment Integration**: Stripe handles payment processing securely and reliably.
* **Hosting**: Railway keeps the platform live and accessible for users.


## **Challenges & Solutions 🎯**

* **Balancing Simplicity with Features**: It was a challenge to make the platform easy to use while integrating all the necessary features for a ticketing platform. The solution started from analyzing each feature to decide where it should fit within the user flow. Some features were built into the navigation bar to find right away, while other were placed in sections that users could explore if they needed them. To keep things simple, clear navigation and breadcrumbs (a way to track where you are in the platform) were used, and related actions were grouped together. This made the platform feel logical and organized, helping users find what they needed without feeling overwhelmed.

* **Security**: Protecting user data and transactions was a top priority, and the main challenge was PCI compliance. Stripe was integrated for secure payment processing, ensuring that sensitive payment information is never stored on the server side. Additionally, Stripe Express accounts provide users with an easy way to track earnings from ticket sales, providing a full financial transparency.

* **Scalability**: As the platform grows, handling an increasing number of users and events becomes essential. One of the challenges was ensuring the platform could scale effectively over time. To ensure scalability, the platform is divided into manageable modules ('apps'), making it easy to add new features. For storage, PostgreSQL was chosen because it can efficiently handle large amounts of data as the platform grows.

---

Eventhub is platform that delivers seamless experience for both event attendees and organizers! 💙
