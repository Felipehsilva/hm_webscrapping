import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3  # <--- Mudança aqui: Usando a lib nativa

# 1. Conectar diretamente ao arquivo (sem precisar do SQLAlchemy create_engine)
# Certifique-se de que o arquivo 'database_hm.sqlite' está na mesma pasta do script
conn = sqlite3.connect('database_hm.sqlite')

# 2. Carregar os dados
query = "SELECT product_price, color_name, cotton, polyester, elastane FROM vitrine"

# Usamos read_sql_query passando a conexão direta do sqlite3
df = pd.read_sql_query(query, conn)

# Fechar a conexão (boa prática)
conn.close()

# --- DICA: Verificando se os dados vieram ---
print(f"Dados carregados: {df.shape[0]} linhas")
print(df.head())

# --- GRÁFICO 1: Distribuição de Preços ---
if not df.empty:
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    sns.histplot(data=df, x='product_price', bins=20, kde=True, color='#2c3e50')
    plt.title('Distribution of Men\'s Jeans Prices (H&M)', fontsize=16)
    plt.xlabel('Price ($)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.tight_layout()
    plt.savefig('price_distribution.png', dpi=300)
    plt.show()

    # --- GRÁFICO 2: Cores Principais ---
    plt.figure(figsize=(10, 6))
    # Pegamos as top 5 cores
    top_colors = df['color_name'].value_counts().head(5)
    
    sns.barplot(x=top_colors.index, y=top_colors.values, palette="Blues_r")
    plt.title('Top 5 Most Common Jeans Colors', fontsize=16)
    plt.ylabel('Number of SKUs', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('color_distribution.png', dpi=300)
    plt.show()
else:
    print("O DataFrame está vazio. Verifique se o banco de dados tem dados.")