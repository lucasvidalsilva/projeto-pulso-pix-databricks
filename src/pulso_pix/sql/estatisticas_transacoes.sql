SELECT
  AnoMes AS ano_mes,
  PAG_PFPJ AS pagador_pf_pj,
  REC_PFPJ AS recebedor_pf_pj,
  PAG_REGIAO AS regiao_pagador,
  REC_REGIAO AS regiao_recebedor,
  PAG_IDADE AS faixa_etaria_pagador,
  REC_IDADE AS faixa_etaria_recebedor,
  FORMAINICIACAO AS forma_iniciacao,
  NATUREZA AS natureza,
  FINALIDADE AS finalidade,
  VALOR AS valor,
  QUANTIDADE AS quantidade,
  extracao_id,
  extraido_em,
  caminho_resposta AS arquivo_origem,
  sha256_resposta AS arquivo_origem_sha256
FROM estatisticas_pix_entrada
