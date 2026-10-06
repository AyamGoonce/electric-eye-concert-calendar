(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3cb1914dbbf8495b.js","sha256":"3cb1914dbbf8495b4ea5fbe0508d8151f52ceb7e25526d878e4f22a4b039c1c6","count":244});
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
