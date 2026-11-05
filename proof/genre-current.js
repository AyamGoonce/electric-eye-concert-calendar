(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.fec050e2004ed7a4.js","sha256":"fec050e2004ed7a48803d287cf5715ef3cf9104faf515d8b1be8566b269d68be","count":244});
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
