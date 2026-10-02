(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.93be4050dadaa6ae.js","sha256":"93be4050dadaa6aedb2192d8184e07156191cfc9d4684483f5ba732cfc2ce3be","count":244});
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
