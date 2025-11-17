import matplotlib.pyplot as plt
import seaborn as sns

def plot_categorical(df, column):
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(x=column, hue='Churn', data=df)
    plt.title(f'Distribuição de {column} vs Churn')
    plt.xlabel(column)
    plt.ylabel('Churn')
    for container in ax.containers:
        ax.bar_label(container)
    plt.show()

def plot_numerical(df, column):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Churn', y=column, data=df)
    plt.title(f'Churn vs {column}')
    plt.xlabel('Churn')
    plt.ylabel(column)
    plt.show()

def plot_hist(df, column):
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x=column, hue='Churn', multiple='stack', bins=30, kde=True)
    plt.title('Distribuição de Tenure vs Churn')
    plt.xlabel('Tempo de Contrato (Meses)')
    plt.ylabel('Frequência')
    plt.show()