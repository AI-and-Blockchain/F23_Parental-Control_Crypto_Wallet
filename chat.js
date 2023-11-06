const url = 'https://api.openai.com/v1/chat/completions';
token = 

async function callAPI(content, fullConvo = [{"role": "system", "content": "you are an AI chat bot that is helping a user learn more about their crypto wallet and crypto currencies as a whole."}]) {
	try {
		fullConvo.push({
			"role": "user",
			"content": content
		});

		const response = await fetch(url, {
			headers: {
				"Content-Type": "application/json",
				"Authorization": `Bearer ${token}`
			},
			body: JSON.stringify({
				"model": "gpt-3.5-turbo",
				"messages": fullConvo
			}),
			method: 'POST'
		});

		console.log(await response.text())
	}
	catch (err) {
		console.error(err);
		return null;
	}
}