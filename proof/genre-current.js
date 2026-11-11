(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.171fe37f25fcc55d.js","sha256":"171fe37f25fcc55d8669233ba11806d7d13f04f45942d8fea053f302cffac8d2","count":244});
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
