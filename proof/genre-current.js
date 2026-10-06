(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ac43cf9bfbe48c18.js","sha256":"ac43cf9bfbe48c18ff860674ffbf2861e0c0fc17a59e1ea3908a9bad01f7ccce","count":244});
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
