const API_URL = import.meta.env.VITE_API_URL;

async function handleResponse(response, errorMessage) {
  if (!response.ok) {
    let message = errorMessage;

    try {
      const errorData = await response.json();
      message = errorData.detail || errorMessage;
    } catch {
      // -----------
    }

    throw new Error(message);
  }

  return response.json();
}


{/* Tickets */}

export async function getTickets() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    throw new Error("User is not authenticated.");
  }
  const response = await fetch(`${API_URL}/tickets/`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch complaints.");
  }

  return data;
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
