def test_pagina_de_admin_responde(client):
    resposta = client.get("/admin/login/")
    assert resposta.status_code == 200
