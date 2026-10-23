// Error message extraction from API responses
//export is JavaScript's way of saying:
//"I want another JavaScript file to be able to use this thing."

 export function getErrorMessage(error) {
  if (typeof error.detail === "string") {
    return error.detail;
  } else if (Array.isArray(error.detail)) {
    return error.detail.map((err) => err.msg).join(". ");
  }
  return "An error occurred. Please try again.";
}

// Show a Bootstrap modal by ID
export function showModal(modalId) {
  const modal = bootstrap.Modal.getOrCreateInstance(
    document.getElementById(modalId),
  );
  modal.show();
  return modal;
}

// Hide a Bootstrap modal by ID
export function hideModal(modalId) {
  const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
  if (modal) modal.hide();
}
// "Give me the ID of a modal. I'll find that HTML element, 
// get its Bootstrap modal object, and if it exists, tell 
// Bootstrap to close it."   



// XSS prevention for dynamic content insertion
export function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
  // So innerHTML is a property that 
  // lets you look at the HTML inside an element.
}

// Date formatting to match server's strftime("%B %d, %Y")
export function formatDate(dateString) {
// Backend
//    ↓
// "2026-09-18T14:30:00"
//    ↓
// new Date(dateString)
//    ↓
// JavaScript Date object
//    ↓
// toLocaleDateString(...)
//    ↓
// "September 18, 2026"
//    ↓
// User sees it
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "2-digit",
  });
}