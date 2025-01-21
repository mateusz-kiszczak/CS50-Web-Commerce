// When the DOM is fully loaded

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Sent email
  document.getElementById('compose-form').addEventListener('submit', (e) => {
    e.preventDefault();
    send_email();
  });

  // Add event listeners to archive buttons
  document.getElementById('email-archive').addEventListener('click', (e) => {
    archiveEmail(sessionStorage.getItem("emailId"));
  });
  document.getElementById('email-unarchive').addEventListener('click', (e) => {
    unarchiveEmail(sessionStorage.getItem("emailId"));
  });
});


// Function to compose email

const compose_email = () => {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Clear messages
  removeAlertMessage();
}


// Function to compose a reply to an email

const compose_reply = (reply) => {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Prepare input values
  let subject = reply.subject;

  if (!subject.includes('Re:')) {
    subject = 'Re: ' + subject;
  }

  let body = 'On ' + reply.timestamp + ' ' + reply.sender + ' wrote: \n\n' + reply.body;

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = reply.sender;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;

  // Clear messages
  removeAlertMessage();
}


// Function to fetch mailbox

const get_mailbox = (mailbox) => {
  let emailsView = document.getElementById('emails-view');

  fetch(`/emails/${mailbox}`)
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      return response.json().then(error => {
        throw new Error(error.error);
      });
    }
  })
  .then(emails => {
    // For each email
    emails.forEach(email => {
      // Create a container element <a>
      let newContainer = document.createElement('div');
      // Add class for styles
      newContainer.setAttribute('class', 'emails__email');
      // Add data attribute with email id as value
      newContainer.setAttribute('data-email-id', email.id);

      // If email was read add extra class
      if (email.read) {
        newContainer.classList.add('emails__email--opened');
      }

      // Create a new element and add SENDER details
      let newSender = document.createElement('div');
      newSender.setAttribute('class', 'emails__email__sender');
      newSender.innerHTML = `<p>${email.sender}</p>`;
      // Add Sender element to the container
      newContainer.appendChild(newSender);

      // Create a new element and add SUBJECT details
      let newSubject = document.createElement('div');
      newSubject.setAttribute('class', 'emails__email__subject');
      newSubject.innerHTML = `<p>${email.subject}</p>`;
      // Add Subject element to the container
      newContainer.appendChild(newSubject);

      // Create a new element and add TIMESTAMP details
      let newTimestamp = document.createElement('div');
      newTimestamp.setAttribute('class', 'emails__email__timestamp');
      newTimestamp.innerHTML = `<p>${email.timestamp}</p>`;
      // Add Timestamp element to the container
      newContainer.appendChild(newTimestamp);

      // Add Event Listener and show email on click
      newContainer.addEventListener('click', (e) => {
        sessionStorage.setItem("emailId", email.id);
        loadEmail(email.id);
      })

      // Finaly, add container element with all the email details to the div with all the emails
      if (email.archived === false && sessionStorage.getItem("mailbox") === 'inbox') {
        emailsView.appendChild(newContainer);
      }
      else if (email.archived === true && sessionStorage.getItem("mailbox") === 'archive') {
        emailsView.appendChild(newContainer);
      }
      else {
        emailsView.appendChild(newContainer);
      }
    });
  })
  .catch(error => {
    console.error('Error:', error.message);
  })
}

// Create an alert with a success or error message when sending na email.
const alertMessage = (message, type) => {
  let newMessageElement = `<div id="compose-alert" class="alert--${type}"><p>${message}</p></div>`;

  // Check if some alert already exists. If yes, remove current alert
  if (document.getElementById('compose-alert')) {
    document.getElementById('compose-alert').remove();
  }
  
  // Add new alert to the page
  let divElement = document.createElement('div');
  divElement.innerHTML = newMessageElement;
  document.getElementById('compose-view').appendChild(divElement.firstChild);
}

const removeAlertMessage = () => {
  // Check if some alert already exists. If yes, remove current alert
  if (document.getElementById('compose-alert')) {
    document.getElementById('compose-alert').remove();
  }
}


const send_email = () => {
  let recipients = document.getElementById('compose-recipients').value;
  let subject = document.getElementById('compose-subject').value;
  let content = document.getElementById('compose-body').value;

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: content
    })
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } 
    else {
      return response.json().then(error => {
        throw new Error(error.error);
      });
    }
  })
  .then(email => {
    console.log(`Email #${email.id} loaded succesfullly.`);

    // Open SENT Mailbox
    removeAlertMessage();
    load_mailbox('sent');
  })
  .catch(error => {
    console.error('Error:', error.message);
  })
}


// Function to load mailbox

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'flex';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';


  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch the emails
  get_mailbox(mailbox);

  // Create a session.
  // Session will be used to remember if user opened an email from inbox, sent or archived
  sessionStorage.setItem("mailbox", `${mailbox}`);
}


// Function to load a single email

const loadEmail = (emailId) => {
  fetch(`/emails/${emailId}`)
  .then(response => {
    if (response.ok) {
      return response.json();
    } 
    else {
      return response.json().then(error => {
        throw new Error(error.error);
      });
    }
  })
  .then(result => {
    alertMessage(result.message, "success");

    // Show the mailbox and hide other views
    document.querySelector('#single-email-view').style.display = 'flex';
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';

    // Check if email was already read and set read to true
    if (result.read === false) {
      fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      })
    }

    // Append email info into the DOM elements
    document.getElementById('email-sender').innerText = result.sender;
    document.getElementById('email-recipients').innerText = result.recipients;
    document.getElementById('email-timestamp').innerText = result.timestamp;
    document.getElementById('email-title').innerText = result.subject;
    document.getElementById('email-body').innerText = result.body;

    // Check if email is archived and manage visible buttons
    if (result.archived === false && sessionStorage.getItem("mailbox") === 'inbox') {
      document.getElementById('email-archive').style.display = 'block';
      document.getElementById('email-unarchive').style.display = 'none';
    }

    if (result.archived === true && sessionStorage.getItem("mailbox") === 'archive') {
      document.getElementById('email-archive').style.display = 'none';
      document.getElementById('email-unarchive').style.display = 'block';
    }

    // Add event listener to REPLY button and pass email's details
    document.getElementById('email-reply').addEventListener('click', () => {
      let replyObj = {
        recipients: result.recipients,
        sender: result.sender,
        subject: result.subject,
        timestamp: result.timestamp,
        body: result.body
      }

      // Open compose email form and pass info
      compose_reply(replyObj);
    });
  })
  .catch(error => {
    alertMessage(error.message, "error");
  })
}

const archiveEmail = (emailId) => {
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: true
    })
  })
  .then(response => {
      // Load mailbox again with updated mails
      load_mailbox('inbox');
  });
}

const unarchiveEmail = (emailId) => {
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: false
    })
  })
  .then(response => {
      // Load mailbox again with updated mails
      load_mailbox('inbox');
  });
}