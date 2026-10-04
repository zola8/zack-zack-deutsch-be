import turso_serverless

if __name__ == '__main__':

    conn = turso_serverless.connect(
        "libsql://dictionary-zola8.aws-eu-west-1.turso.io",
        auth_token="",
    )

    for row in conn.execute("SELECT * FROM dictionary_entries LIMIT 10"):
        print(row)

    conn.close()
