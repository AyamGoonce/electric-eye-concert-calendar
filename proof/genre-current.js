(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.bd625d183d9abeaa.js","sha256":"bd625d183d9abeaa4ea7d47fc66331b129b76889baa4a592e1a888d55266d997","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
