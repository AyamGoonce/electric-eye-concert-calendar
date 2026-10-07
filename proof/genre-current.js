(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a1620fa76e9dbc2c.js","sha256":"a1620fa76e9dbc2cd230673131222775708e865497d5152769a9cbd0d7d4a9f2","count":244});
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
