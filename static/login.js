// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCvf0qZzwKa27X7wXbTAIN8HgcR4-yhoG0",
  authDomain: "hack-a-sol-399d1.firebaseapp.com",
  projectId: "hack-a-sol-399d1",
  storageBucket: "hack-a-sol-399d1.appspot.com",
  messagingSenderId: "658095024603",
  appId: "1:658095024603:web:c0d3354d5e17bfc7309ffe",
  measurementId: "G-M5TRT2F9TF"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const authForm = document.getElementById("auth-form-element");
const authTitle = document.getElementById("auth-title");
const toggleAuth = document.getElementById("toggle-auth");
const submitButton = document.getElementById("submit-button");

let isSignUp = true;

authForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (isSignUp) {
    createUserWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in
        const user = userCredential.user;
        console.log("User signed up:", user);
      })
      .catch((error) => {
        console.error("Error signing up:", error.message);
      });
  } else {
    signInWithEmailAndPassword(auth, email, password)
      .then((userCredential) => {
        // Signed in
        const user = userCredential.user;
        console.log("User logged in:", user);
      })
      .catch((error) => {
        console.error("Error logging in:", error.message);
      });
  }
});

toggleAuth.addEventListener("click", (e) => {
  e.preventDefault();
  isSignUp = !isSignUp;
  authTitle.textContent = isSignUp ? "Sign Up" : "Log In";
  submitButton.textContent = isSignUp ? "Sign Up" : "Log In";
  toggleAuth.textContent = isSignUp ? "Log In" : "Sign Up";
});
