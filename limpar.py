from app import conectar

conexao = conectar()
conexao.execute("DELETE FROM documentos")
conexao.commit()
conexao.close()
print("Documentos apagados.")
