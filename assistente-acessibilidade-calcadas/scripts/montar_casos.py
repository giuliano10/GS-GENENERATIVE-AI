"""Gera avaliacao/casos_teste.jsonl e avaliacao/lora_treino.jsonl.

Cada pergunta respondível aponta para o(s) trecho(s) do gabarito por uma ÂNCORA: um pedaço
literal do texto da lei. O script procura a âncora em base/trechos.jsonl e falha se ela
não existir — assim o gabarito nunca aponta para um artigo errado, mesmo que a base seja
remontada e os ids mudem.

Formato de cada linha:
  id, pergunta, tipo ("consta" | "nao_consta"), categoria, resposta_gabarito,
  palavras_chave (lista de grupos; cada grupo = alternativas, TODOS os grupos precisam aparecer),
  trechos_gabarito (ids)
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.avaliacao import contem_palavras_chave  # noqa: E402

TRECHOS = [json.loads(l) for l in open(RAIZ / "base/trechos.jsonl", encoding="utf-8")]
NAO = "Não consta na base de conhecimento."


def _corpo(t):
    """Texto do trecho sem o caput/inciso repetidos (linhas iniciais terminadas em '[...]')."""
    linhas = t["texto"].split("\n")
    while linhas and linhas[0].endswith("[...]"):
        linhas = linhas[1:]
    return "\n".join(linhas)


def achar(ancora: str) -> str:
    achados = [t["id"] for t in TRECHOS if ancora in _corpo(t)]
    if len(achados) != 1:
        raise SystemExit(f"Âncora {ancora!r} encontrada em {achados} (esperado exatamente 1)")
    return achados[0]


def C(pid, cat, pergunta, resposta, chaves, *ancoras):
    return {"id": pid, "pergunta": pergunta, "tipo": "consta", "categoria": cat,
            "resposta_gabarito": resposta, "palavras_chave": chaves,
            "trechos_gabarito": [achar(a) for a in ancoras]}


def N(pid, pergunta, motivo):
    return {"id": pid, "pergunta": pergunta, "tipo": "nao_consta", "categoria": "nao_consta",
            "resposta_gabarito": NAO, "motivo_nao_consta": motivo, "palavras_chave": [],
            "trechos_gabarito": []}


M120 = ["1,20", "1,2 m", "1,2m", "1.20", "um metro e vinte"]
PROIBIDO = ["proibid", "vedad", "nao pode", "nao e permitido", "nao sao permitid", "nao poderao", "nao deve"]

# ===========================================================================
# CONJUNTO DE TESTE (nunca usado no treino nem na escolha do limiar)
# ===========================================================================
TESTE = [
    C("T01", "dimensoes", "Qual a largura mínima da faixa livre da calçada em São Paulo?",
      "A faixa livre deve ter largura mínima de 1,20 m (Decreto 59.671/2020, art. 4º, I, g).",
      [M120], "g) ter largura mínima de 1,20m"),
    C("T02", "dimensoes", "Qual a inclinação transversal máxima permitida na faixa livre da calçada?",
      "A inclinação transversal da faixa livre deve ser constante e de no máximo 3%.",
      [["3%", "3 %", "tres por cento"]],
      "c) ter inclinação transversal constante e não superior a 3%", "preservando-se a inclinação máxima de 3%"),
    C("T03", "dimensoes", "Qual a largura mínima da faixa de serviço da calçada?",
      "A faixa de serviço deve ter largura mínima de 70 cm.",
      [["70", "0,70", "setenta"]], "c) ter largura mínima de 70cm"),
    C("T04", "dimensoes", "Qual a altura livre mínima que placas de sinalização e toldos retráteis devem respeitar sobre a faixa livre?",
      "Instalações como placas, abas de mobiliário e toldos retráteis devem ficar a no mínimo 2,10 m do nível da calçada.",
      [["2,10", "2,1 m", "2,1m", "dois metros e dez"]], "de, no mínimo, 2,10m"),
    C("T05", "dimensoes", "A partir de que largura a calçada pode ter faixa de acesso?",
      "A faixa de acesso só existe em calçadas com mais de 2 m de largura.",
      [["2 m", "2m", "dois metros", "2,00"]], "exclusivamente nas calçadas com mais de 2m"),
    C("T06", "dimensoes", "Em calçadas com mais de 2,40 m, quanto da largura total deve ser faixa livre?",
      "A faixa livre deve corresponder a no mínimo 50% da largura total da calçada.",
      [["50%", "50 %", "metade", "cinquenta por cento"]], "h) corresponder a, no mínimo, 50%"),
    C("T07", "esquinas", "Até que distância da esquina a calçada deve ficar livre de interferências visuais ou físicas?",
      "As esquinas devem ficar livres de interferências até 5 m a partir do bordo do alinhamento da via transversal.",
      [["5 m", "5m", "cinco metros"]], "até a distância de 5m"),
    C("T08", "acesso_veiculos", "Qual a extensão máxima da testada do imóvel que pode ter guia rebaixada para entrada de carros?",
      "O rebaixamento de guia para acesso de veículos não pode exceder 50% da testada do imóvel (com exceção de residências unifamiliares).",
      [["50%", "50 %", "metade", "cinquenta por cento"]], "não poderá exceder a 50%"),
    C("T09", "acesso_veiculos", "Posso rebaixar a guia na esquina para fazer a entrada da minha garagem?",
      "Não. É vedado o rebaixamento de guias nas esquinas para acesso de veículos.",
      [PROIBIDO], "É vedado o rebaixamento de guias nas esquinas"),
    C("T10", "acesso_veiculos", "Qual deve ser a altura do degrau separador no rebaixamento de guia para veículos?",
      "Deve haver 1 degrau separador entre a sarjeta e o rebaixamento, com altura de 3 cm a 5 cm.",
      [["3 cm", "3cm", "3 a 5", "tres"], ["5 cm", "5cm", "cinco centimetros"]], "com altura de 3cm"),
    C("T11", "responsabilidade", "Quem é responsável por construir e conservar a calçada em frente a um imóvel particular em São Paulo?",
      "O proprietário do imóvel (ou o possuidor, o titular do domínio útil ou o condomínio), que responde solidariamente.",
      [["proprietario"]], "a) o proprietário do imóvel;"),
    C("T12", "materiais", "Quais materiais são autorizados para o pavimento das calçadas em São Paulo?",
      "Concreto moldado in loco, peças e placas de concreto pré-fabricadas de alto desempenho, mistura asfáltica tipo Gap Graded e outros materiais definidos pela autoridade.",
      [["concreto"], ["asfalt", "gap graded"]], "I - concreto moldado"),
    C("T13", "responsabilidade", "Quando uma calçada é considerada em mau estado de conservação?",
      "Quando tem buracos, ondulações, desníveis não exigidos pelo logradouro ou obstáculos que impeçam a circulação livre e segura, ou reparos fora do padrão da calçada.",
      [["buraco"], ["ondula", "desnive", "obstaculo"]], "II - em mau estado de manutenção"),
    C("T14", "mobiliario", "Onde devem ser instalados bancos, lixeiras e postes na calçada?",
      "Fora da faixa livre: preferencialmente na faixa de serviço e, excepcionalmente, na faixa de acesso.",
      [["faixa de servico"]], "I - não poderão ser instalados na faixa livre;"),
    C("T15", "mobiliario", "A que distância da esquina deve ficar uma banca de jornal ou quiosque?",
      "Equipamentos de grande porte devem ficar a no mínimo 15 m do bordo do alinhamento da via transversal, a 50 cm da guia e só em calçadas com mais de 3,50 m.",
      [["15 m", "15m", "quinze metros"]], "a, no mínimo, 15m"),
    C("T16", "mobiliario", "A que distância da esquina devem ficar lixeiras, caixas de correio e paraciclos?",
      "Preferencialmente a no mínimo 5 m do bordo do alinhamento da via transversal e a 50 cm da guia.",
      [["5 m", "5m", "cinco metros"]], "VII - quando se tratar de equipamentos de pequeno porte"),
    C("T17", "situacoes_atipicas", "Qual a largura mínima da faixa livre junto a um poste ou árvore quando a calçada é estreita?",
      "Na transposição de obstáculos isolados de até 40 cm (postes, árvores), a faixa livre deve ter no mínimo 80 cm.",
      [["80", "0,80", "oitenta"]], "largura mínima de 80cm"),
    C("T18", "drenagem", "Qual a abertura máxima das frestas de grelhas de drenagem na calçada?",
      "As frestas das grelhas devem ter no máximo 1,5 cm, transversais ao fluxo de pedestres.",
      [["1,5", "um e meio", "15 mm"]], "no máximo, 1,5cm"),
    C("T19", "situacoes_atipicas", "Quando a calçada pode ter degraus?",
      "Quando a declividade longitudinal passa de 12%, e só dentro das faixas de serviço ou de acesso.",
      [["12%", "12 %", "doze por cento"]], "superior a 12%"),
    C("T20", "dimensoes", "Qual a largura mínima de calçada para permitir ciclofaixa ou compartilhamento com bicicletas?",
      "2,90 m, preservando a faixa livre de 1,20 m.",
      [["2,90", "2,9 m", "2,9m", "dois metros e noventa"]], "largura mínima de 2,90m"),
    C("T21", "vegetacao", "Depois que a Prefeitura corta uma árvore que estragou a calçada, qual o prazo para o responsável consertar?",
      "30 dias a partir do corte ou supressão da árvore.",
      [["30", "trinta"]], "terá o prazo de 30 (trinta) dias"),
    C("T22", "vegetacao", "Em que parte da calçada as árvores devem ser plantadas?",
      "Dentro das faixas de acesso ou de serviço.",
      [["servico"]], "o plantio de árvores deverá ser efetuado dentro das faixas de acesso ou de serviço"),
    C("T23", "estacionamento", "É permitido estacionar o carro sobre a calçada em São Paulo?",
      "Não. O Estatuto do Pedestre proíbe estacionar qualquer veículo sobre calçadas e faixas de pedestres, e o CTB trata como infração grave.",
      [PROIBIDO + ["infracao"]],
      "Fica proibido o estacionamento de quaisquer veículos", "VIII - no passeio ou sobre faixa destinada a pedestre"),
    C("T24", "iluminacao", "Qual a iluminação mínima exigida nas calçadas pelo Estatuto do Pedestre?",
      "Pelo menos 10 lux, medidos no nível do piso no ponto de menor luminosidade.",
      [["10 lux", "dez lux", "10 (dez) lux"]], "com pelo menos 10 (dez) lux, medidos ao nível do piso da faixa"),
    C("T25", "iluminacao", "Qual a iluminação mínima nas faixas de pedestre de vias estruturais?",
      "Pelo menos 32 lux, medidos no nível do piso no ponto de menor luminosidade.",
      [["32", "trinta e dois"]], "32 (trinta e dois) lux"),
    C("T26", "penalidades", "Qual a multa para concessionária que mantém poste irregular na calçada depois de notificada?",
      "Multa de R$ 50.000,00 por dia, por face de quadra, até a regularização (além de advertência).",
      [["50.000", "50 mil", "cinquenta mil"]], "multa de R$ 50.000,00"),
    C("T27", "pedestre", "Quais são os deveres do pedestre segundo o Estatuto do Pedestre de São Paulo?",
      "Cumprir o estatuto, respeitar a sinalização e usar faixas e passarelas, atravessar de forma segura, ajudar crianças, idosos e pessoas com dificuldade de locomoção e andar pelo acostamento onde não houver calçada.",
      [["faixa", "sinaliza"], ["atravess", "ajudar", "acostamento"]], "Art. 10. São deveres do pedestre"),
    C("T28", "travessia", "A partir de que distância o pedestre é obrigado a usar a faixa de pedestres?",
      "Deve usar a faixa sempre que ela existir a até 50 metros dele.",
      [["50", "cinquenta"]], "numa distância de até cinqüenta metros"),
    C("T29", "travessia", "Se o semáforo abrir para os carros no meio da minha travessia, quem tem a preferência?",
      "O pedestre que ainda não concluiu a travessia tem preferência, mesmo com o sinal verde para os veículos.",
      [["preferencia", "prioridade"]],
      "será dada preferência aos pedestres que não tenham concluído a travessia",
      "II - que não haja concluído a travessia mesmo que ocorra sinal verde"),
    C("T30", "infracoes", "Estacionar na calçada é que tipo de infração de trânsito?",
      "Infração grave, com multa e remoção do veículo (CTB, art. 181, VIII).",
      [["grave"]], "VIII - no passeio ou sobre faixa destinada a pedestre"),
    C("T31", "infracoes", "Qual a infração para quem anda com o carro em cima da calçada?",
      "Infração gravíssima, com multa multiplicada por três (CTB, art. 193).",
      [["gravissima"]], "Art. 193. Transitar com o veículo em calçadas"),
    C("T32", "infracoes", "Estacionar em vaga de pessoa com deficiência sem credencial é infração de qual gravidade?",
      "Gravíssima, com multa e remoção do veículo (CTB, art. 181, XX).",
      [["gravissima"]], "XX - nas vagas reservadas às pessoas com deficiência"),
    C("T33", "pedestre", "O ciclista que desce da bicicleta e a empurra é considerado pedestre?",
      "Sim. O ciclista desmontado empurrando a bicicleta equipara-se ao pedestre em direitos e deveres.",
      [["pedestre"]], "O ciclista desmontado empurrando a bicicleta"),
    C("T34", "pedestre", "Onde o pedestre deve andar numa rua urbana que não tem calçada?",
      "Pelos bordos da pista de rolamento, em fila única, com prioridade sobre os veículos (salvo locais proibidos ou inseguros).",
      [["bordo", "beira", "lateral", "borda"], ["fila unica"]], "Nas áreas urbanas, quando não houver passeios"),
    C("T35", "vagas", "Qual a porcentagem de vagas de estacionamento reservadas para pessoas com deficiência?",
      "2% do total de vagas, garantida no mínimo 1 vaga sinalizada.",
      [["2%", "2 %", "dois por cento"]],
      "deverão ser em número equivalente a dois por cento", "devem equivaler a 2% (dois por cento) do total",
      "serão reservados, pelo menos, dois por cento do total de vagas"),
    C("T36", "transporte", "Que porcentagem da frota de táxis deve ser acessível?",
      "10% dos veículos das frotas de táxi devem ser acessíveis à pessoa com deficiência.",
      [["10%", "10 %", "dez por cento"]], "As frotas de empresas de táxi devem reservar 10%"),
    C("T37", "transporte", "Locadoras de veículos precisam ter carro adaptado para pessoa com deficiência?",
      "Sim, 1 veículo adaptado a cada conjunto de 20 veículos da frota.",
      [["20", "vinte"]], "a cada conjunto de 20 (vinte) veículos"),
    C("T38", "obras", "Quem deve garantir a circulação segura das pessoas durante obras em calçadas e vias públicas?",
      "O poder público e as empresas concessionárias responsáveis pelas obras, durante e após a execução.",
      [["poder publico"], ["concessionaria"]],
      "Em qualquer intervenção nas vias e nos espaços públicos, o poder público",
      "Em qualquer intervenção nas vias e logradouros públicos, o Poder Público"),
    C("T39", "sinalizacao", "Onde os semáforos para pedestres são obrigados a ter sinal sonoro?",
      "Em vias públicas de grande circulação ou que dão acesso a serviços de reabilitação.",
      [["grande circulacao", "reabilitacao"]], "Os semáforos para pedestres instalados em vias públicas de grande circulação"),
    C("T40", "sinalizacao", "Como deve ser sinalizado um mobiliário urbano que oferece risco de acidente para pessoas com deficiência?",
      "Com sinalização tátil de alerta no piso, de acordo com as normas técnicas.",
      [["tatil"]], "Art. 10-A. A instalação de qualquer mobiliário urbano"),
    C("T41", "definicoes", "Para que serve o passeio público segundo a Lei 10.098?",
      "Destina-se somente à circulação de pedestres e, quando possível, à implantação de mobiliário urbano e vegetação.",
      [["pedestre"], ["mobiliario", "vegetacao"]], "O passeio público, elemento obrigatório de urbanização"),
    C("T42", "mobilidade_urbana", "Qual a prioridade entre modos de transporte definida pela Política Nacional de Mobilidade Urbana?",
      "Prioridade dos modos não motorizados sobre os motorizados e do transporte público coletivo sobre o individual motorizado.",
      [["nao motorizad"], ["coletivo"]], "II - prioridade dos modos de transportes não motorizados"),
    C("T43", "mobilidade_urbana", "Quais municípios são obrigados a ter Plano de Mobilidade Urbana?",
      "Municípios com mais de 20 mil habitantes, os de regiões metropolitanas/aglomerações com mais de 1 milhão de habitantes e os de áreas de interesse turístico.",
      [["20.000", "20 mil", "vinte mil"]], "I - com mais de 20.000 (vinte mil) habitantes"),
    C("T44", "sinalizacao", "O planejamento das vias públicas precisa prever piso tátil?",
      "Sim. O Decreto 5.296/2004 inclui a instalação de piso tátil direcional e de alerta entre as exigências de acessibilidade das vias.",
      [["tatil"]], "III - a instalação de piso tátil direcional e de alerta"),
    C("T45", "definicoes", "Quem é considerado pessoa com mobilidade reduzida?",
      "Quem tem dificuldade de movimentação, permanente ou temporária, incluindo idoso, gestante, lactante, pessoa com criança de colo e obeso.",
      [["gestante", "idoso", "obeso", "lactante", "crianca de colo"]],
      "IX - pessoa com mobilidade reduzida", "IV - pessoa com mobilidade reduzida"),
    # ----------------------------- não consta -----------------------------
    N("T46", "Qual o valor em reais da multa por estacionar o carro na calçada?",
      "A base classifica a infração (grave), mas o valor em reais está no art. 258 do CTB, que não foi incluído."),
    N("T47", "Qual o valor da multa, em reais, para o proprietário que não conserta a calçada em São Paulo?",
      "Os valores estão no Anexo da Lei 15.442/2011, que não está na base."),
    N("T48", "Quais as dimensões do piso tátil de alerta, como largura e altura do relevo?",
      "Está na NBR 16537 (ABNT), norma paga que não está na base."),
    N("T49", "Qual a velocidade máxima permitida em vias locais segundo o CTB?",
      "Art. 61 do CTB, fora dos artigos selecionados."),
    N("T50", "Qual o valor da tarifa do ônibus municipal em São Paulo?", "Tarifa vigente não está em nenhuma lei da base."),
    N("T51", "Quantos segundos, no mínimo, o sinal verde para pedestres deve durar?",
      "O Estatuto do Pedestre só fala em tempo 'suficiente'; não há número."),
    N("T52", "Por quanto tempo vale a credencial de estacionamento para pessoa com deficiência?",
      "A LBI diz que é válida em todo o território nacional, mas não fala de prazo."),
    N("T53", "A partir de que idade a pessoa idosa tem direito a vaga reservada de estacionamento?",
      "Está no Estatuto do Idoso, fora da base."),
    N("T54", "Qual a largura mínima de uma ciclofaixa pintada na pista de rolamento?",
      "A base só fala de ciclofaixa compartilhada na calçada (calçada de 2,90 m), não da largura da ciclofaixa."),
    N("T55", "Qual decreto municipal regulamenta os aplicativos de transporte como Uber em São Paulo?",
      "A PNMU diz que o município regulamenta, mas o decreto municipal não está na base."),
    N("T56", "Quantos quilômetros de ciclovias existem em São Paulo hoje?", "Dado estatístico fora da base."),
    N("T57", "Qual o prazo para a Prefeitura responder uma reclamação sobre calçada feita pelo 156?",
      "O decreto só diz que reclamações vão pelos canais de atendimento; não há prazo."),
    N("T58", "Qual a altura máxima permitida para o muro na frente de uma casa em São Paulo?",
      "Código de Obras, fora da base."),
    N("T59", "Qual a pena de prisão para quem estaciona em vaga de idoso?", "Não existe na base (e é infração administrativa)."),
    N("T60", "Qual a inclinação máxima de uma rampa de acesso dentro de um prédio comercial?",
      "Parâmetro da NBR 9050, fora da base; o decreto de SP só trata de rampas na calçada."),
]

# ===========================================================================
# PERGUNTAS DE TREINO (LoRA) E DE CALIBRAÇÃO DO LIMIAR — fatos diferentes do teste
# ===========================================================================
TREINO = [
    C("R01", "dimensoes", "Qual a inclinação máxima da rampa de acomodação para acesso ao imóvel na faixa de acesso?",
      "A rampa de acomodação na faixa de acesso pode ter inclinação transversal de no máximo 8,33%.",
      [["8,33"]], "d) rampa de acomodação para acesso ao imóvel"),
    C("R02", "esquinas", "Qual a distância mínima entre a entrada de veículos de um lote de esquina e o encontro dos alinhamentos?",
      "O acesso de veículos em lote de esquina deve ficar a no mínimo 6 m do ponto de encontro dos alinhamentos (salvo residência unifamiliar e habitações agrupadas onde não for possível).",
      [["6 m", "6m", "seis metros"]], "deverá distar, no mínimo, 6m"),
    C("R03", "situacoes_atipicas", "Em calçadas estreitas, qual a largura mínima da faixa livre junto a guias rebaixadas ou mobiliário?",
      "Pode ser reduzida para no mínimo 90 cm, com inclinação transversal máxima de 2%, junto a essas interferências.",
      [["90", "0,90", "noventa"]], "largura mínima de 90cm"),
    C("R04", "dimensoes", "Qual a altura livre mínima de interferências construtivas sobre a faixa livre?",
      "No mínimo 3 m acima do nível da calçada.",
      [["3 m", "3m", "tres metros"]], "no mínimo, 3m (três metros)"),
    C("R05", "dimensoes", "Como se mede a largura total de uma calçada?",
      "Do alinhamento do lote até o bordo externo da guia.",
      [["alinhamento"], ["guia"]], "§ 2º A largura total das calçadas é medida"),
    C("R06", "dimensoes", "Em quantas faixas a calçada deve ser organizada em São Paulo?",
      "Prioritariamente em 3 faixas: faixa livre, faixa de serviço e faixa de acesso (ou 2, se a largura não permitir).",
      [["3", "tres"]], "As calçadas deverão ser prioritariamente organizadas em 3"),
    C("R07", "travessia", "Em ruas de pouco movimento sem faixa de pedestre, precisa ter rebaixamento de guia na esquina?",
      "Sim. Em ruas de baixo volume de tráfego devem ser previstos rebaixamentos junto às esquinas mesmo sem faixa de pedestres.",
      [["sim", "devem", "deverao"]], "Em ruas de baixo volume de tráfego"),
    C("R08", "travessia", "Pode haver degrau entre o fim do rebaixamento de guia da travessia e a rua?",
      "Não. Não deve haver desnível entre o término do rebaixamento e a pista, incluída a sarjeta.",
      [PROIBIDO + ["nao deve haver"]], "Não deverá haver desnível entre o término"),
    C("R09", "responsabilidade", "Quem faz as guias e sarjetas da rua?",
      "É competência da Administração Pública Municipal, que pode autorizar o particular a executá-las.",
      [["municip", "prefeitura"]], "A execução de guias e sarjetas é de competência"),
    C("R10", "materiais", "Calçadas na frente de imóveis tombados podem usar materiais diferentes?",
      "Sim, desde que em consonância com a legislação de patrimônio histórico.",
      [["patrimonio", "tombad"]], "As calçadas localizadas em frente ou em área envoltória de bens tombados"),
    C("R11", "obras", "Depois de quebrar a calçada para uma obra, como a faixa livre deve ser refeita?",
      "Em toda a sua seção transversal, sem emendas ou reparos longitudinais, respeitando a modulação do piso.",
      [["toda", "inteira"]], "I - nas obras que exijam quebra da calçada"),
    C("R12", "responsabilidade", "Além da Prefeitura, quem pode executar ou reformar calçadas?",
      "Profissionais e empresas capacitadas, associações de moradores ou ONGs em regime de mutirão, além dos responsáveis pelos imóveis.",
      [["mutirao", "associac", "empresa"]], "Art. 17. Além da Administração Pública Municipal"),
    C("R13", "obras", "Reforma de calçada precisa de responsável técnico?",
      "Sim, deve haver Anotação ou Registro de Responsabilidade Técnica (ART/RRT).",
      [["responsabilidade tecnica", "rrt"]], "Anotação ou Registro de Responsabilidade Técnica"),
    C("R14", "vegetacao", "Quem deve cuidar da manutenção de uma calçada verde?",
      "O munícipe, na extensão dos limites do seu lote.",
      [["municipe", "morador", "proprietario"]], "O munícipe será responsável pela manutenção"),
    C("R15", "vegetacao", "Posso fazer calçada verde em rua que tem feira livre?",
      "Só com autorização da Subprefeitura.",
      [["subprefeitura"]], "Nos logradouros onde são realizadas feiras livres"),
    C("R16", "responsabilidade", "Quando uma calçada é considerada inexistente?",
      "Quando foi executada em desconformidade com as normas técnicas vigentes na data da sua construção ou reconstrução.",
      [["desconformidade", "fora das normas", "em desacordo"]], "I - inexistente, quando executada"),
    C("R17", "responsabilidade", "Onde faço reclamação sobre calçada irregular em São Paulo?",
      "Pelos canais de atendimento ao cidadão da Prefeitura de São Paulo.",
      [["atendimento"]], "As reclamações e a prestação de informações"),
    C("R18", "definicoes", "Quais princípios a execução e manutenção de calçadas em São Paulo devem seguir?",
      "Acessibilidade e desenho universal; sustentabilidade; eficiência, eficácia e efetividade; segurança nos deslocamentos; e equidade no uso do espaço.",
      [["desenho universal", "acessibilidade"]], "I - acessibilidade e desenho universal;"),
    C("R19", "definicoes", "Quem é pedestre para o decreto de calçadas de São Paulo?",
      "Pessoa que anda ou está a pé, em cadeira de rodas ou conduzindo bicicleta na qual não esteja montada.",
      [["cadeira de rodas", "a pe"]], "X - pedestre: pessoa que anda ou está a pé"),
    C("R20", "pedestre", "A quem se estendem os direitos do Estatuto do Pedestre além de quem anda a pé?",
      "A quem usa cadeira de rodas, conduz carrinho de bebê ou de pacotes, ao ciclista desmontado e aos trabalhadores de coleta e varrição.",
      [["cadeira de rodas", "carrinho"]], "§ 1º Os direitos e deveres estabelecidos nesta lei estendem-se"),
    C("R21", "penalidades", "Qual a multa para imóvel com vagas no recuo que não demarcar o limite com a calçada?",
      "R$ 2.000,00, aplicada mensalmente enquanto durar a infração.",
      [["2.000", "2 mil", "dois mil"]], "multa de R$ 2.000,00"),
    C("R22", "penalidades", "Qual o prazo que as concessionárias tiveram para adaptar ou retirar postes irregulares das calçadas?",
      "90 dias a contar da publicação do Estatuto do Pedestre.",
      [["90", "noventa"]], "deverão, no prazo de 90 (noventa) dias"),
    C("R23", "iluminacao", "Qual a iluminação mínima nas esquinas de vias locais?",
      "Pelo menos 15 lux, medidos no nível do piso no eixo das vias.",
      [["15", "quinze"]], "com pelo menos 15 (quinze) lux"),
    C("R24", "pedestre", "Quando é a Semana do Pedestre em São Paulo?",
      "Na terceira semana do mês de julho.",
      [["julho"]], "terceira semana do mês de julho"),
    C("R25", "pedestre", "Motos de entrega podem circular em calçadões exclusivos de pedestres?",
      "Não. É vedado; o infrator é multado e, na reincidência, o equipamento é apreendido.",
      [PROIBIDO], "É vedado o trânsito de ciclomotor"),
    C("R26", "mobilidade_urbana", "Em que raio em volta de estações de transporte o desenho para pedestres deve ser compatibilizado?",
      "Em um raio mínimo de 300 m.",
      [["300"]], "raio mínimo de 300m"),
    C("R27", "sinalizacao", "O pedestre tem direito a semáforo com contagem regressiva?",
      "Sim, onde a demanda justificar: sinais inteligentes com temporizadores numéricos decrescentes e alerta sonoro quando necessário.",
      [["temporizador", "contagem", "regressiv", "decrescente"]], "VIII - sinais de trânsito luminosos de tecnologia inteligente"),
    C("R28", "travessia", "Quando se deve usar passarela em vez de travessia em nível?",
      "Só quando a topografia, rios ou a necessidade de atravessar vias expressas ou rodovias exigirem por questões técnicas.",
      [["topografia", "rio", "via expressa", "rodovia"]], "XI - travessias respeitando sua lógica"),
    C("R29", "infracoes", "Estacionar a menos de 5 metros da esquina é infração?",
      "Sim, infração média, com multa e remoção do veículo.",
      [["media"]], "I - nas esquinas e a menos de cinco metros"),
    C("R30", "infracoes", "Estacionar em frente a guia rebaixada de garagem é infração?",
      "Sim, infração média, com multa e remoção do veículo.",
      [["media"]], "IX - onde houver guia de calçada (meio-fio) rebaixada"),
    C("R31", "infracoes", "Qual a infração do motorista que não dá preferência ao pedestre na faixa?",
      "Infração gravíssima, com multa (CTB, art. 214, I).",
      [["gravissima"]], "Art. 214. Deixar de dar preferência"),
    C("R32", "infracoes", "O que é proibido ao pedestre pelo CTB e qual a penalidade?",
      "Andar na pista, atravessar fora da faixa ou em viadutos e cruzamentos, desobedecer à sinalização etc.; infração leve, multa de 50% do valor da infração leve.",
      [["leve"]], "Art. 254. É proibido ao pedestre"),
    C("R33", "pedestre", "Quem é responsável pela segurança dos pedestres no trânsito?",
      "Os veículos: os maiores pelos menores, os motorizados pelos não motorizados e, juntos, pela incolumidade dos pedestres.",
      [["veiculo"]], "§ 2º Respeitadas as normas de circulação e conduta"),
    C("R34", "obras", "Se a calçada estiver obstruída por uma obra, o que deve ser feito?",
      "O órgão com circunscrição sobre a via deve garantir sinalização e proteção para a circulação dos pedestres.",
      [["sinaliza"]], "§ 6º Onde houver obstrução da calçada"),
    C("R35", "travessia", "Quem deve manter as faixas de pedestres em boas condições?",
      "O órgão ou entidade com circunscrição sobre a via, garantindo visibilidade, higiene, segurança e sinalização.",
      [["orgao", "entidade"]], "Art. 71. O órgão ou entidade com circunscrição"),
    C("R36", "estacionamento", "Carro pode passar por cima da calçada?",
      "Só para entrar ou sair de imóveis ou de áreas especiais de estacionamento.",
      [["imove", "estacionamento"]], "V - o trânsito de veículos sobre passeios, calçadas"),
    C("R37", "vagas", "A credencial de estacionamento para pessoa com deficiência vale em outros estados?",
      "Sim, é vinculada à pessoa com deficiência e válida em todo o território nacional.",
      [["todo o territorio", "nacional"]], "§ 4º A credencial a que se refere o § 2º"),
    C("R38", "transporte", "O taxista pode cobrar mais caro de passageiro com deficiência?",
      "Não. É proibida a cobrança diferenciada de tarifas ou valores adicionais.",
      [PROIBIDO], "É proibida a cobrança diferenciada"),
    C("R39", "transporte", "Quais itens o carro adaptado de locadora deve ter no mínimo?",
      "Câmbio automático, direção hidráulica, vidros elétricos e comandos manuais de freio e embreagem.",
      [["cambio automatico"]], "câmbio automático, direção hidráulica"),
    C("R40", "definicoes", "O que são barreiras atitudinais?",
      "Atitudes ou comportamentos que impeçam ou prejudiquem a participação social da pessoa com deficiência em igualdade de condições.",
      [["atitude", "comportamento"]], "e) barreiras atitudinais"),
    C("R41", "definicoes", "Qual o símbolo nacional de identificação de pessoas com deficiências ocultas?",
      "O cordão de fita com desenhos de girassóis (uso opcional).",
      [["girass"]], "cordão de fita com desenhos de girassóis"),
    C("R42", "eventos", "Quantos banheiros químicos acessíveis um evento precisa ter?",
      "No mínimo 10% do total, com pelo menos 1 unidade acessível.",
      [["10%", "10 %", "dez por cento"]], "O número mínimo de banheiros químicos acessíveis"),
    C("R43", "lazer", "Que porcentagem dos brinquedos de parques deve ser adaptada?",
      "No mínimo 5% de cada brinquedo e equipamento de lazer, tanto quanto tecnicamente possível.",
      [["5%", "5 %", "cinco por cento"]], "No mínimo 5% (cinco por cento) de cada brinquedo"),
    C("R44", "mobilidade_urbana", "Como a Política Nacional de Mobilidade Urbana define acessibilidade?",
      "Facilidade disponibilizada às pessoas que possibilite a todos autonomia nos deslocamentos desejados.",
      [["autonomia"]], "III - acessibilidade: facilidade disponibilizada"),
    C("R45", "mobilidade_urbana", "Que informações o usuário de transporte tem direito de receber nos pontos de ônibus?",
      "Informações gratuitas e acessíveis sobre itinerários, horários, tarifas e integração com outros modais.",
      [["itinerario", "horario"]], "III - ser informado nos pontos de embarque e desembarque"),
    C("R46", "edificacoes", "Qual prazo os prédios públicos já existentes tiveram para se tornar acessíveis pelo Decreto 5.296?",
      "Trinta meses a contar da publicação do decreto.",
      [["30", "trinta"]], "terão elas prazo de trinta meses a contar da data de publicação deste Decreto para garantir acessibilidade"),
    C("R47", "edificacoes", "Os elevadores precisam indicar o andar em braile?",
      "Sim, junto às botoeiras externas deve estar sinalizado em braile em qual andar a pessoa se encontra.",
      [["braile", "braille"]], "sinalizado em braile em qual andar"),
    # ----------------------------- não consta -----------------------------
    N("R48", "Qual o valor da passagem do metrô de São Paulo?", "Fora da base."),
    N("R49", "Qual a cor obrigatória do piso tátil de alerta?", "NBR 16537, fora da base."),
    N("R50", "A partir de que idade o idoso tem gratuidade no ônibus municipal?", "Fora da base."),
    N("R51", "Qual a altura padrão da guia (meio-fio) em São Paulo?", "Fora da base."),
    N("R52", "Qual o horário do rodízio municipal de veículos em São Paulo?", "Fora da base."),
    N("R53", "Quantas estações tem a linha 4-Amarela do metrô?", "Fora da base."),
    N("R54", "Qual a velocidade máxima na Avenida Paulista?", "Fora da base."),
    N("R55", "Qual a largura mínima de uma ciclovia bidirecional?", "Fora da base."),
    N("R56", "Qual o prazo para a Prefeitura tapar um buraco no asfalto?", "Fora da base."),
    N("R57", "Qual o valor do IPTU de uma casa na Zona Sul?", "Fora da base."),
    N("R58", "Quantas vagas de bicicleta um prédio residencial novo precisa ter?", "Fora da base."),
    N("R59", "Qual a validade da carteira de motorista?", "Fora da base."),
    N("R60", "Qual a altura máxima de um degrau de escada dentro de edifícios?", "NBR 9050, fora da base."),
    N("R61", "O que a LGPD diz sobre câmeras de segurança em condomínios?", "Fora da base."),
    N("R62", "Qual o horário de funcionamento das feiras livres em São Paulo?", "Fora da base."),
]


def checar(lista):
    ids = [c["id"] for c in lista]
    assert len(ids) == len(set(ids))
    for c in lista:
        # o gabarito precisa satisfazer as próprias palavras-chave (sanidade do avaliador)
        if c["tipo"] == "consta":
            for g in c["palavras_chave"]:
                assert contem_palavras_chave(c["resposta_gabarito"], [g]), (c["id"], g)


if __name__ == "__main__":
    checar(TESTE)
    checar(TREINO)
    assert not {c["pergunta"] for c in TESTE} & {c["pergunta"] for c in TREINO}
    for nome, lista in [("casos_teste.jsonl", TESTE), ("lora_treino.jsonl", TREINO)]:
        with open(RAIZ / "avaliacao" / nome, "w", encoding="utf-8") as f:
            for c in lista:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        n = sum(c["tipo"] == "consta" for c in lista)
        print(f"{nome}: {len(lista)} perguntas ({n} constam, {len(lista) - n} não constam)")
