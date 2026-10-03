(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.bae126c342a360f9.js","sha256":"bae126c342a360f93d412e8e6ffcd0f59cfcc408678b0f23c91ed596e9e8a3b6","count":244});
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
