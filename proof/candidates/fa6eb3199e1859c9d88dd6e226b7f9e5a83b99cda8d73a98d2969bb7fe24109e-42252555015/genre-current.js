(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6ad410459fde0c2f.js","sha256":"6ad410459fde0c2fb0dbd9236d4cf6958b118ea40a4f1c855d16a1ee2ed79331","count":244});
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
