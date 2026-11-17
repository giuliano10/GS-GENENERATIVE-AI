# Erros de rag_lora

### T01 (consta, dimensoes)
- Pergunta: Qual a largura mínima da faixa livre da calçada em São Paulo?
- Gabarito: A faixa livre deve ter largura mínima de 1,20 m (Decreto 59.671/2020, art. 4º, I, g). | trechos ['SP-D59671-art4-p2']
- Recuperados: ['SP-D59671-art26', 'SP-D59671-art24', 'SP-D59671-art4-p2'] (score top1 0.7209987484223911)
- Saída bruta: `{"resposta": "Deve ser de pelo menos 1,20m (um metro e vinte centímetros).", "fontes": ["SP-D59671-art26"], "recusa": false}`
- Correção: {'id': 'T01', 'tipo': 'consta', 'categoria': 'dimensoes', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 3.026}

### T05 (consta, dimensoes)
- Pergunta: A partir de que largura a calçada pode ter faixa de acesso?
- Gabarito: A faixa de acesso só existe em calçadas com mais de 2 m de largura. | trechos ['SP-D59671-art4-p2']
- Recuperados: ['SP-D59671-art4-p2', 'SP-D59671-art24', 'SP-D59671-art22'] (score top1 0.6661986253019455)
- Saída bruta: `{"resposta": "Só se a largura for maior que 2 m e não permitir a implantação da faixa livre.", "fontes": ["SP-D59671-art24"], "recusa": false}`
- Correção: {'id': 'T05', 'tipo': 'consta', 'categoria': 'dimensoes', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 3.052}

### T07 (consta, esquinas)
- Pergunta: Até que distância da esquina a calçada deve ficar livre de interferências visuais ou físicas?
- Gabarito: As esquinas devem ficar livres de interferências até 5 m a partir do bordo do alinhamento da via transversal. | trechos ['SP-D59671-art5']
- Recuperados: ['SP-D59671-art5', 'SP-D59671-art4-p1', 'SP-D59671-art24'] (score top1 0.6585722780637434)
- Saída bruta: `{"resposta": "Aqui está o trecho relevante:", 
 "fontes": ["SP-D59671-art5"],
 "recusa": false}`
- Correção: {'id': 'T07', 'tipo': 'consta', 'categoria': 'esquinas', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': True, 'citacao_fora_contexto': False, 'latencia_s': 2.292}

### T08 (consta, acesso_veiculos)
- Pergunta: Qual a extensão máxima da testada do imóvel que pode ter guia rebaixada para entrada de carros?
- Gabarito: O rebaixamento de guia para acesso de veículos não pode exceder 50% da testada do imóvel (com exceção de residências unifamiliares). | trechos ['SP-D59671-art10']
- Recuperados: ['SP-D59671-art10', 'SP-D59671-art24', 'SP-L16673-art19'] (score top1 0.6442177683973509)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T08', 'tipo': 'consta', 'categoria': 'acesso_veiculos', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 1.661}

### T09 (consta, acesso_veiculos)
- Pergunta: Posso rebaixar a guia na esquina para fazer a entrada da minha garagem?
- Gabarito: Não. É vedado o rebaixamento de guias nas esquinas para acesso de veículos. | trechos ['SP-D59671-art10']
- Recuperados: ['SP-D59671-art10', 'SP-L16673-art19', 'L10098-art11'] (score top1 0.6143533461337556)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T09', 'tipo': 'consta', 'categoria': 'acesso_veiculos', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 0.012}

### T12 (consta, materiais)
- Pergunta: Quais materiais são autorizados para o pavimento das calçadas em São Paulo?
- Gabarito: Concreto moldado in loco, peças e placas de concreto pré-fabricadas de alto desempenho, mistura asfáltica tipo Gap Graded e outros materiais definidos pela autoridade. | trechos ['SP-D59671-art13']
- Recuperados: ['SP-D59671-art16-p1', 'SP-D59671-art13', 'SP-D59671-art12'] (score top1 0.688881501180929)
- Saída bruta: `{"resposta": "Concreto moldado, "in loco", com armadura metálica e juntas de dilatação; peças e placas de concreto pré-fabricadas de alto desempenho; mistura asfáltica Gap Graded; outros materiais conforme especificações técnicas.", "fontes": ["SP-D59671-art13"], "recusa": false}`
- Correção: {'id': 'T12', 'tipo': 'consta', 'categoria': 'materiais', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': False, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 6.258}

### T15 (consta, mobiliario)
- Pergunta: A que distância da esquina deve ficar uma banca de jornal ou quiosque?
- Gabarito: Equipamentos de grande porte devem ficar a no mínimo 15 m do bordo do alinhamento da via transversal, a 50 cm da guia e só em calçadas com mais de 3,50 m. | trechos ['SP-D59671-art20-p1']
- Recuperados: ['SP-D59671-art20-p2', 'SP-D59671-art20-p1', 'SP-D59671-art5'] (score top1 0.6206496079623146)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T15', 'tipo': 'consta', 'categoria': 'mobiliario', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 0.018}

### T16 (consta, mobiliario)
- Pergunta: A que distância da esquina devem ficar lixeiras, caixas de correio e paraciclos?
- Gabarito: Preferencialmente a no mínimo 5 m do bordo do alinhamento da via transversal e a 50 cm da guia. | trechos ['SP-D59671-art20-p2']
- Recuperados: ['SP-D59671-art20-p2', 'SP-D59671-art5', 'SP-D59671-art20-p1'] (score top1 0.6574276713317545)
- Saída bruta: `{"resposta": "Em pontos de parada de transporte coletivo, são dispensadas das disposições do artigo 20, mas deve-se preservar a faixa livre e a rota acessível.", "fontes": ["SP-D59671-art20-p2"], "recusa": false}`
- Correção: {'id': 'T16', 'tipo': 'consta', 'categoria': 'mobiliario', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': True, 'citacao_fora_contexto': False, 'latencia_s': 4.885}

### T17 (consta, situacoes_atipicas)
- Pergunta: Qual a largura mínima da faixa livre junto a um poste ou árvore quando a calçada é estreita?
- Gabarito: Na transposição de obstáculos isolados de até 40 cm (postes, árvores), a faixa livre deve ter no mínimo 80 cm. | trechos ['SP-D59671-art24']
- Recuperados: ['SP-D59671-art24', 'SP-D59671-art26', 'SP-D59671-art4-p2'] (score top1 0.7095197277014305)
- Saída bruta: `{"resposta": "A largura mínima será de 80 cm, com inclinação máxima de 2%. ", "fontes": ["SP-D59671-art26"], "recusa": false}`
- Correção: {'id': 'T17', 'tipo': 'consta', 'categoria': 'situacoes_atipicas', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 2.858}

### T18 (consta, drenagem)
- Pergunta: Qual a abertura máxima das frestas de grelhas de drenagem na calçada?
- Gabarito: As frestas das grelhas devem ter no máximo 1,5 cm, transversais ao fluxo de pedestres. | trechos ['SP-D59671-art21']
- Recuperados: ['SP-D59671-art21', 'SP-D59671-art2-p4', 'SP-D59671-art24'] (score top1 0.6391317321997237)
- Saída bruta: `{"resposta": "No máximo 1,5 cm transversalmente ao sentido do fluxo de pedestres.", "fontes": ["SP-D59671-art2-p4"], "recusa": false}`
- Correção: {'id': 'T18', 'tipo': 'consta', 'categoria': 'drenagem', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 2.826}

### T20 (consta, dimensoes)
- Pergunta: Qual a largura mínima de calçada para permitir ciclofaixa ou compartilhamento com bicicletas?
- Gabarito: 2,90 m, preservando a faixa livre de 1,20 m. | trechos ['SP-D59671-art4-p4']
- Recuperados: ['SP-D59671-art4-p4', 'SP-D59671-art24', 'SP-D59671-art26'] (score top1 0.6804333590509601)
- Saída bruta: `{"resposta": "Fora do limite mínimo de 2,90m, deve-se garantir a presença de pelo menos 1,20m de faixa livre, com inclinação máxima de 2%.", "fontes": ["SP-D59671-art24"], "recusa": false}`
- Correção: {'id': 'T20', 'tipo': 'consta', 'categoria': 'dimensoes', 'acerto': True, 'alucinacao': False, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 4.803}

### T23 (consta, estacionamento)
- Pergunta: É permitido estacionar o carro sobre a calçada em São Paulo?
- Gabarito: Não. O Estatuto do Pedestre proíbe estacionar qualquer veículo sobre calçadas e faixas de pedestres, e o CTB trata como infração grave. | trechos ['SP-L16673-art22', 'L9503-art181-p2']
- Recuperados: ['SP-D59671-art27', 'SP-L16673-art22', 'SP-D59671-art23'] (score top1 0.6324650839785346)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T23', 'tipo': 'consta', 'categoria': 'estacionamento', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 1.475}

### T24 (consta, iluminacao)
- Pergunta: Qual a iluminação mínima exigida nas calçadas pelo Estatuto do Pedestre?
- Gabarito: Pelo menos 10 lux, medidos no nível do piso no ponto de menor luminosidade. | trechos ['SP-L16673-art11']
- Recuperados: ['SP-L16673-art1', 'SP-D59671-art26', 'SP-L16673-art6'] (score top1 0.6723404853728693)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T24', 'tipo': 'consta', 'categoria': 'iluminacao', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 1.677}

### T25 (consta, iluminacao)
- Pergunta: Qual a iluminação mínima nas faixas de pedestre de vias estruturais?
- Gabarito: Pelo menos 32 lux, medidos no nível do piso no ponto de menor luminosidade. | trechos ['SP-L16673-art11']
- Recuperados: ['SP-L16673-art11', 'SP-D59671-art33', 'SP-L16673-art9-p1'] (score top1 0.6741547028611935)
- Saída bruta: `{"resposta": "Nove (9) luxes, medidos no nível do piso no ponto de menor luminosidade.", "fontes": ["SP-L16673-art9-p1"], "recusa": false}`
- Correção: {'id': 'T25', 'tipo': 'consta', 'categoria': 'iluminacao', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 3.629}

### T28 (consta, travessia)
- Pergunta: A partir de que distância o pedestre é obrigado a usar a faixa de pedestres?
- Gabarito: Deve usar a faixa sempre que ela existir a até 50 metros dele. | trechos ['L9503-art69']
- Recuperados: ['L9503-art69', 'SP-L16673-art12', 'SP-L16673-art10'] (score top1 0.6350702618042164)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T28', 'tipo': 'consta', 'categoria': 'travessia', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 1.698}

### T31 (consta, infracoes)
- Pergunta: Qual a infração para quem anda com o carro em cima da calçada?
- Gabarito: Infração gravíssima, com multa multiplicada por três (CTB, art. 193). | trechos ['L9503-art193']
- Recuperados: ['L9503-art193', 'L9503-art181-p2', 'L9503-art181-p1'] (score top1 0.6380092031223287)
- Saída bruta: `{"resposta": "Não consta na base de conhecimento.", "fontes": [], "recusa": true}`
- Correção: {'id': 'T31', 'tipo': 'consta', 'categoria': 'infracoes', 'acerto': False, 'alucinacao': False, 'recusa_indevida': True, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 1.643}

### T33 (consta, pedestre)
- Pergunta: O ciclista que desce da bicicleta e a empurra é considerado pedestre?
- Gabarito: Sim. O ciclista desmontado empurrando a bicicleta equipara-se ao pedestre em direitos e deveres. | trechos ['L9503-art68-p1']
- Recuperados: ['SP-L16673-art2-p1', 'L9503-art68-p1', 'SP-D59671-art2-p3'] (score top1 0.6387606212445625)
- Saída bruta: `{"resposta": "Sim, segundo o Código de Trânsito Brasileiro.", "fontes": ["L9503-art68-p1"], "recusa": false}`
- Correção: {'id': 'T33', 'tipo': 'consta', 'categoria': 'pedestre', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': True, 'citacao_fora_contexto': False, 'latencia_s': 2.575}

### T44 (consta, sinalizacao)
- Pergunta: O planejamento das vias públicas precisa prever piso tátil?
- Gabarito: Sim. O Decreto 5.296/2004 inclui a instalação de piso tátil direcional e de alerta entre as exigências de acessibilidade das vias. | trechos ['D5296-art15']
- Recuperados: ['D5296-art15', 'SP-D59671-art11', 'SP-L16673-art11'] (score top1 0.6475492469611637)
- Saída bruta: `{"resposta": "Sim, inclui-se na condição estabelecida no caput.", "fontes": ["D5296-art15"], "recusa": false}`
- Correção: {'id': 'T44', 'tipo': 'consta', 'categoria': 'sinalizacao', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': True, 'citacao_fora_contexto': False, 'latencia_s': 3.092}

### T45 (consta, definicoes)
- Pergunta: Quem é considerado pessoa com mobilidade reduzida?
- Gabarito: Quem tem dificuldade de movimentação, permanente ou temporária, incluindo idoso, gestante, lactante, pessoa com criança de colo e obeso. | trechos ['L13146-art3-p4', 'L10098-art2-p2']
- Recuperados: ['L10098-art2-p2', 'D5296-art5-p3', 'L13146-art3-p4'] (score top1 0.6438318973839349)
- Saída bruta: `{"resposta": "Aquele que tem dificuldade de movimentar-se, permanente ou temporariamente, gerando redução efetiva da mobilidade, flexibilidade, coordenação motora e percepção.", "fontes": ["D5296-art5-p3"], "recusa": false}`
- Correção: {'id': 'T45', 'tipo': 'consta', 'categoria': 'definicoes', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': False, 'citacao_fora_contexto': False, 'latencia_s': 4.516}

### T47 (nao_consta, nao_consta)
- Pergunta: Qual o valor da multa, em reais, para o proprietário que não conserta a calçada em São Paulo?
- Gabarito: Não consta na base de conhecimento. | trechos []
- Recuperados: ['SP-L16673-art16', 'SP-D59671-art34-p2', 'SP-D59671-art1-p1'] (score top1 0.6378161254356761)
- Saída bruta: `{"resposta": "R$ 50.000,00 por dia, até a cessação da irregularidade.", "fontes": ["SP-D59671-art34-p2"], "recusa": false}`
- Correção: {'id': 'T47', 'tipo': 'nao_consta', 'categoria': 'nao_consta', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 3.17}

### T52 (nao_consta, nao_consta)
- Pergunta: Por quanto tempo vale a credencial de estacionamento para pessoa com deficiência?
- Gabarito: Não consta na base de conhecimento. | trechos []
- Recuperados: ['L13146-art47', 'L13146-art51', 'L10098-art12-a'] (score top1 0.6685793848636242)
- Saída bruta: `{"resposta": "Vale durante todo o período em que a pessoa tem o benefício de acesso, geralmente até 1 ano após a obtenção do documento.", "fontes": ["L13146-art47"], "recusa": false}`
- Correção: {'id': 'T52', 'tipo': 'nao_consta', 'categoria': 'nao_consta', 'acerto': False, 'alucinacao': True, 'recusa_indevida': False, 'json_valido': True, 'citacao_correta': None, 'citacao_fora_contexto': False, 'latencia_s': 3.262}
