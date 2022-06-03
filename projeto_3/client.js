window.onload = () => {
	console.log("window loaded");
};

function connect() {
	var sse_establish_connection = document.getElementById("sse");
	console.log(sse_establish_connection.value);
	if (sse_establish_connection.innerHTML == "No") {
		// cria a conexao persistente
		var eventSource = new EventSource("http://127.0.0.1:8000/stream");

		eventSource.onerror = (event, err) => {
			console.error("Error in connect SSE", event, err);
		};

		// define um evento para executar quando o servidor envia uma mensagem
		eventSource.addEventListener("message", (e) => {
			console.log("received event", e);
			var data = JSON.parse(e.data);
			var message =
				"servidor  " +
				data.modo +
				" o recurso " +
				data.recurso +
				" ao cliente: " +
				data.nome;
			var targetContainer = document.getElementById("data");
			var data_filtered = message + "<br />";
			targetContainer.innerHTML += data_filtered;
		});

		// conexao estabelecida, pode receber mensagens do servidor
		console.log("Connected");

		sse_establish_connection.innerHTML = "Yes";
	}
}

function getToken() {
	// recupera o recurso com POST
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
}

function releaseToken() {
	// libera o recurso com PUT
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
