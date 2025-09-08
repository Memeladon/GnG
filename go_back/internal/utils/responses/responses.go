package responses

import (
	"encoding/json"
	"net/http"
)

func Simple(w http.ResponseWriter, data any, err error) {
	type simpleResponse struct {
		Data  any    `json:"data,omitempty"`
		Error string `json:"error,omitempty"`
	}

	payload := simpleResponse{
		Data: data,
	}
	if err != nil {
		payload.Error = err.Error()
	}

	if err := json.NewEncoder(w).Encode(&payload); err != nil {
		http.Error(w, "could not parse server output", http.StatusInternalServerError)
	}
}
