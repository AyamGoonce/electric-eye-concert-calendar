(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.4e616bb6dcbf9f9b.js","sha256":"4e616bb6dcbf9f9bf904a2b973273626f825426748760de305ac0a743ea9034b","count":244});
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
