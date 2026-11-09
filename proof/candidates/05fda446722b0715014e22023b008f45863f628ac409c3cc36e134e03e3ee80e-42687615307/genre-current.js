(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.10145d6191e1a75b.js","sha256":"10145d6191e1a75b0e59b22c5e752cc7a0096474f26de05f509ffe697ade9f94","count":244});
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
