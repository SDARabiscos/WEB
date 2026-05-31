export interface DadosVeiculo {
  placa: string;
  marca: string;
  modelo: string;
  generico: string;
  ano: string;
  anoModelo: string;
  cor: string;
  combustivel: string;
  potencia: string;
  chassi: string;
  uf: string;
  municipio: string;
  importado: string;
  codigoFipe: string;
  modeloFipe: string;
  valorFipe: string;
  placaAntiga: string;
  fonte: string;
}

export interface DadosIpva {
  valorVenal: string;
  aliquota: string;
  valorIpva: string;
  historico: { ano: string; valorVenal: string; valorIpva: string }[];
}

export interface EstadoIpva {
  estado: string;
  valorVenal: string;
  taxa: string;
  valorIpva: string;
}
