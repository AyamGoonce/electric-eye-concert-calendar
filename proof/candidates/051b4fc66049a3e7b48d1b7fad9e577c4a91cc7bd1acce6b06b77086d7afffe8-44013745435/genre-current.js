(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7cc122ca6f23663a.js","sha256":"7cc122ca6f23663a0245d2c7c2988f61451e753aae3b56c986e3439b5447f28f","count":244});
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
