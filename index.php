<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Auto-Claim</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f5f5f5; }
    .container { width: 600px; margin: 30px auto; background:#fff; padding:20px; border-radius:8px; }
    h2 { color:#333; }
    label { display:block; margin-top:10px; }
    input, select { width:100%; padding:8px; margin-top:5px; }
    .btn { margin-top:15px; padding:10px; background:#007bff; color:#fff; border:none; cursor:pointer; }
    .btn:hover { background:#0056b3; }
  </style>
</head>
<body>
  <div class="container">
    <h2>Gestion des comptes</h2>
    <form method="post" action="">
      <label>Email *</label>
      <input type="email" name="email" placeholder="exemple@mail.com" required>

      <label>Mot de passe *</label>
      <input type="password" name="password" placeholder="Votre mot de passe" required>

      <label>Attente avant réclamation (min:sec) *</label>
      <input type="text" name="attente" placeholder="mm:ss">

      <label>Base URL *</label>
      <input type="text" name="baseurl" value="tronpick.io">

      <label>Proxy</label>
      <input type="text" name="proxy" placeholder="socks5h://user:pass@127.0.0.1:1080">

      <label>
        <input type="checkbox" name="auto_game"> Activer le Game Auto
      </label>

      <button type="submit" class="btn">+ Ajouter le compte</button>
    </form>

    <?php
      if ($_SERVER["REQUEST_METHOD"] == "POST") {
        echo "<h3>Compte ajouté :</h3>";
        echo "Email : " . htmlspecialchars($_POST["email"]) . "<br>";
        echo "Mot de passe : " . htmlspecialchars($_POST["password"]) . "<br>";
        echo "Attente : " . htmlspecialchars($_POST["attente"]) . "<br>";
        echo "Base URL : " . htmlspecialchars($_POST["baseurl"]) . "<br>";
        echo "Proxy : " . htmlspecialchars($_POST["proxy"]) . "<br>";
        echo "Game Auto : " . (isset($_POST["auto_game"]) ? "Oui" : "Non") . "<br>";
      }
    ?>
  </div>
</body>
</html>
