//Script para obtener las ids de transiciones de un ticket en Jira las ids de cada columna
const fetch = require("node-fetch");

const issueKey = "P001470-11670"; //Numero de ticket

const credenciales = `Basic ${Buffer.from("").toString("base64")}`;
fetch(``, {
  method: "GET",
  headers: {
    Authorization: credenciales,
    Accept: "application/json",
  },
})
  .then(response => response.json())
  .then(data => {
    console.log(`Ids de las columnas para el ticket ${issueKey}:\n`);
    data.transitions.forEach(t => {
      console.log(`- ${t.name} (ID: ${t.id})`);
    });
  })
  .catch(err => console.error("Error:", err));
