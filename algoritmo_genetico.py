def gerar_populacao_inicial(dados, tamanho_pop, tamanho_problema):
    populacao = []
    for _ in range(tamanho_pop):
        cronograma, _ = gerar_solucao_inicial_aleatoria(dados, tamanho_problema)
        populacao.append({
            "cronograma": cronograma,
            "fitness": avalia(cronograma)
        })
    return populacao


def avalia(cronograma):
    tempos_finais = [op["Fim"] for op in cronograma]
    return max(tempos_finais)


def selecao(populacao, k=3):
    candidatos = random.sample(populacao, k)
    return min(candidatos, key=lambda ind: ind["fitness"])


def crossover(pai1, pai2, dados):
    ponto = len(pai1["cronograma"]) // 2
    filho_ops = pai1["cronograma"][:ponto] + pai2["cronograma"][ponto:]
    
    # reconstruir cronograma válido
    maquina_ops = construir_lista_por_maquina(dados)
    cronograma = construir_cronograma(dados, maquina_ops)
    
    return {
        "cronograma": cronograma,
        "fitness": avalia(cronograma)
    }


def mutacao(individuo, dados):
    maquina_ops = construir_lista_por_maquina(dados)
    vizinho = gerar_vizinho(maquina_ops)
    cronograma = construir_cronograma(dados, vizinho)
    return {
        "cronograma": cronograma,
        "fitness": avalia(cronograma)
    }


def algoritmo_genetico(dados, tamanho_problema, tamanho_pop=20, geracoes=50, taxa_mutacao=0.2):
    populacao = gerar_populacao_inicial(dados, tamanho_pop, tamanho_problema)

    for _ in range(geracoes):
        nova_populacao = []
        for _ in range(tamanho_pop):
            pai1 = selecao(populacao)
            pai2 = selecao(populacao)
            filho = crossover(pai1, pai2, dados)
            
            if random.random() < taxa_mutacao:
                filho = mutacao(filho, dados)
            
            nova_populacao.append(filho)
        
        populacao = nova_populacao
    
    melhor = min(populacao, key=lambda ind: ind["fitness"])
    return melhor["cronograma"], melhor["fitness"]
