SELECT
  ano_mes,
  natureza,
  forma_iniciacao,
  regiao_pagador,
  regiao_recebedor,
  SUM(valor) AS valor_total,
  SUM(quantidade) AS quantidade_total
FROM estatisticas_pix_silver_mes
GROUP BY
  ano_mes,
  natureza,
  forma_iniciacao,
  regiao_pagador,
  regiao_recebedor
