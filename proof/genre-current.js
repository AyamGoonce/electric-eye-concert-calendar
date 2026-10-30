(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5e9e87ab3f92a018.js","sha256":"5e9e87ab3f92a018eccd86d2b9cc0ab9cc7001acce2fb986a176df1529613a35","count":244});
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
