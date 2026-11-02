
export default function ComplaintResults({
  result,
  playingAudio,
  activeAudioText,
  onPlayAudio,
  onStopAudio,
}) {
  if (!result) return null;

  // Support both a list of tickets and a single response object.
  const complaints = Array.isArray(result)
    ? result
    : Array.isArray(result.tickets)
      ? result.tickets
      : [result];

  return (
    <div className="mt-8 space-y-5">
      {complaints.map((complaint, index) => {
        const aiResponse = complaint.ai_response;
        const isPlaying =
          playingAudio && activeAudioText === aiResponse;

        return (
          <div
            key={complaint.ticket_id || complaint._id || index}
            className="space-y-5 rounded-xl border border-gray-200 p-5"
          >
            {/* Complaint title */}
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">
                {complaints.length > 1
                  ? `Complaint #${complaint.ticket_id}`
                  : "Complaint Result"}
              </h2>
            </div>

            {/* Complaint description */}
            {(complaint.issue_description ||
              complaint.complaint ||
              complaint.text) && (
              <div className="rounded-xl bg-gray-50 p-5">
                <p className="text-sm font-semibold text-gray-500">
                  Complaint Details
                </p>
                <p className="mt-2 text-gray-800">
                  {complaint.issue_description ||
                    complaint.complaint ||
                    complaint.text}
                </p>
              </div>
            )}

            {/* AI Response */}
            {aiResponse && (
              <div className="rounded-xl bg-blue-50 p-5">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-blue-700">
                    AI Assistant
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      isPlaying
                        ? onStopAudio()
                        : onPlayAudio(aiResponse)
                    }
                    className="rounded-full bg-white p-2 shadow-sm transition hover:bg-gray-100"
                    title={
                      isPlaying
                        ? "Stop response"
                        : "Listen to response"
                    }
                  >
                    {isPlaying ? "⏹" : "🔊"}
                  </button>
                </div>

                <p className="mt-3 text-gray-800">{aiResponse}</p>
              </div>
            )}

            {/* Classification Details */}
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {complaint.category && (
                <div className="rounded-xl border border-gray-200 p-4">
                  <p className="text-xs font-medium text-gray-500">
                    Category
                  </p>
                  <p className="mt-1 font-medium text-gray-800">
                    {complaint.category ||
                      complaint.predicted_category}
                  </p>
                </div>
              )}

              {complaint.confidence !== undefined &&
                complaint.confidence !== null && (
                  <div className="rounded-xl border border-gray-200 p-4">
                    <p className="text-xs font-medium text-gray-500">
                      Confidence
                    </p>
                    <p className="mt-1 font-medium text-gray-800">
                      {(Number(complaint.confidence) * 100).toFixed(1)}%
                    </p>
                  </div>
                )}

              {complaint.sentiment && (
                <div className="rounded-xl border border-gray-200 p-4">
                  <p className="text-xs font-medium text-gray-500">
                    Sentiment
                  </p>
                  <p className="mt-1 font-medium capitalize text-gray-800">
                    {complaint.sentiment}
                  </p>
                </div>
              )}

              {complaint.priority && (
                <div className="rounded-xl border border-gray-200 p-4">
                  <p className="text-xs font-medium text-gray-500">
                    Priority
                  </p>
                  <p className="mt-1 font-medium capitalize text-gray-800">
                    {complaint.priority}
                  </p>
                </div>
              )}

              {(complaint.routing_team || complaint.assigned_team) && (
                <div className="rounded-xl border border-gray-200 p-4 sm:col-span-2">
                  <p className="text-xs font-medium text-gray-500">
                    Assigned Team
                  </p>
                  <p className="mt-1 font-medium text-gray-800">
                    {complaint.routing_team || complaint.assigned_team}
                  </p>
                </div>
              )}
            </div>

            {/* Ticket ID */}
            {(complaint.ticket_id || complaint._id) && (
              <div className="rounded-xl bg-green-50 p-4">
                <p className="text-sm font-medium text-green-700">
                  Complaint submitted successfully.
                </p>
                <p className="mt-1 break-all text-xs text-green-600">
                  Ticket ID: #{complaint.ticket_id || complaint._id}
                </p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}