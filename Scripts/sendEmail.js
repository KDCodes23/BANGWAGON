const nodemailer = require("nodemailer");
const sgMail = require("@sendgrid/mail");

sgMail.setApiKey("YOUR_SENDGRID_API_KEY");

const msg = {
  to: "recipient@example.com",
  from: "your-email@example.com",
  subject: "Hello from SendGrid!",
  text: "This is a test email sent via SendGrid API.",
};

sgMail
  .send(msg)
  .then(() => console.log("Email sent successfully!"))
  .catch((error) => console.error(error));
