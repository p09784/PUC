# Requisitos Funcionais - Plataforma InkSpot

Abaixo estão listados os Requisitos Funcionais do projeto InkSpot, baseados no formato exigido pela disciplina.

---

**Identificador**: RF0001
**Nome**: Cadastro de Usuários
**Descrição / Regras**: 
- O sistema deve permitir que novos usuários se cadastrem escolhendo o tipo de conta: "Cliente" ou "Tatuador".
- É obrigatório o preenchimento dos campos nome, e-mail, senha (com no mínimo 6 caracteres) e cidade.
- O sistema não deve permitir o cadastro de um e-mail já existente na base de dados.
**Informações/dados**: 
- Nome
- E-mail
- Senha
- Tipo de Conta
- Cidade

---

**Identificador**: RF0002
**Nome**: Login no Sistema
**Descrição / Regras**: 
- O usuário deverá estar previamente cadastrado no sistema para realizar o login.
- Caso as credenciais sejam inválidas, o sistema deve apresentar uma mensagem de erro (com animação visual) e impedir o acesso.
- Após o login bem-sucedido, a barra de navegação deve ser atualizada para mostrar a área do usuário logado.
**Informações/dados**: 
- E-mail
- Senha

---

**Identificador**: RF0003
**Nome**: Busca e Filtragem de Artistas
**Descrição / Regras**: 
- O usuário deve poder buscar tatuadores por nome do artista ou por estilos específicos (ex: Realismo, Aquarela, Old School).
- O sistema deve possuir um campo para busca por Localização informando o CEP ou nome da cidade.
- O sistema deve disponibilizar um botão para buscar artistas usando a "Localização Atual" do usuário (geolocalização).
- Os resultados devem ser atualizados em tempo real na tela.
**Informações/dados**: 
- Termo de busca (nome, estilo)
- CEP ou Cidade
- Coordenadas de Localização Atual

---

**Identificador**: RF0004
**Nome**: Visualização do Perfil e Portfólio do Tatuador
**Descrição / Regras**: 
- Ao clicar em um artista na busca, o sistema deve abrir os detalhes do perfil do tatuador.
- O perfil deve exibir os dados de apresentação: Nome, biografia, anos de experiência, estilos, valor cobrado por hora e nota de avaliação média.
- O sistema deve exibir uma galeria de fotos com os trabalhos anteriores do artista.
**Informações/dados**: 
- ID do Artista

---

**Identificador**: RF0005
**Nome**: Assinatura de Planos (Para Tatuadores)
**Descrição / Regras**: 
- Tatuadores devem possuir uma página dedicada para visualizar os benefícios e assinar planos de divulgação (Básico, Pro, Estúdio).
- A contratação de um plano deve liberar funcionalidades exclusivas, como destaque nas buscas e portfólio ilimitado.
**Informações/dados**: 
- Plano Escolhido
- Dados de Pagamento (futuro)

---

**Identificador**: RF0006
**Nome**: Contato Direto (Agendamento)
**Descrição / Regras**: 
- O sistema deve fornecer um botão de "Entrar em Contato" no perfil do tatuador.
- Ao clicar, o usuário (cliente) deve ser redirecionado para o WhatsApp do tatuador escolhido para facilitar o agendamento da sessão.
**Informações/dados**: 
- Número de telefone do tatuador
- Mensagem padrão de saudação

---

**Identificador**: RF0007
**Nome**: Alternância de Tema (Acessibilidade Visual)
**Descrição / Regras**: 
- O sistema deve permitir que o usuário alterne a interface entre o "Modo Claro" (fundo branco) e o "Modo Escuro" (fundo preto).
- A escolha do usuário deve ser salva no navegador (via localStorage) para que seja mantida nas próximas visitas.
**Informações/dados**: 
- Preferência de tema (Claro/Escuro)
