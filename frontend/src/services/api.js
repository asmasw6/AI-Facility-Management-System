const API_URL = import.meta.env.VITE_API_URL;

async function handleResponse(response, errorMessage) {
  if (!response.ok) {
    let message = errorMessage;

    try {
      const errorData = await response.json();
      message = errorData.detail || errorMessage;
    } catch {
      // Keep default error message
    }

    throw new Error(message);
  }

  return response.json();
}


{/* Tickets */}

export async function getTickets() {
  const response = await fetch(`${API_URL}/tickets/`);

  return handleResponse(
    response,
    "Failed to fetch complaints."
  );
}


export async function getTicket(ticketId) {
  const response = await fetch(`${API_URL}/tickets/${ticketId}`);

  return handleResponse(
    response,
    "Failed to fetch complaint."
  );
}


export async function updateTicket(ticketId, data) {
  const response = await fetch(`${API_URL}/tickets/${ticketId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return handleResponse(
    response,
    "Failed to update complaint."
  );
}

{/* Customers */}

export async function getCustomer(customerId) {
  const response = await fetch(`${API_URL}/customers/${customerId}`);

  return handleResponse(
    response,
    "Failed to fetch customer."
  );
}
