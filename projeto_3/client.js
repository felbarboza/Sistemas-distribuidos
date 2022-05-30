window.onload = () => {
	console.log("window loaded");
};

function getToken() {
	var name = document.getElementById("name").value;
	var resource = document.getElementById("resource").value;

	body = {
		name,
		resource,
	};

	fetch("http://127.0.0.1:8000/resource", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(body),
	})
		.then((response) => {
			console.log(response);
		})
		.catch((err) => {
			console.error(err);
		});

	var eventSource = new EventSource("http://127.0.0.1:8000/stream");

	eventSource.onerror = (event, err) => {
		console.error("Error in connect SSE", event, err);
	};

	eventSource.addEventListener("message", (e) => {
		console.log("received event", e);
		var data = JSON.parse(e.data);
		var message =
			"servidor  " + data.modo + " o recurso ao cliente: " + data.nome;
		var targetContainer = document.getElementById("data");
		var data_filtered = message + "<br />";
		targetContainer.innerHTML += data_filtered;
	});

	console.log("Connected");
}

function releaseToken() {
	var name = document.getElementById("name").value;

	body = {
		name,
	};

	fetch("http://127.0.0.1:8000/resource", {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(body),
	})
		.then((response) => {
			console.log(response);
		})
		.catch((err) => {
			console.error(err);
		});
}
