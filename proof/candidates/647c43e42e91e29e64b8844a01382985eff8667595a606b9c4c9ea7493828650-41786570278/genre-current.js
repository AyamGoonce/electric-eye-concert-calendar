(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3555676fde27acfd.js","sha256":"3555676fde27acfd149f375adb5fbc376825202f23e7726cb6112ab661dd9db5","count":244});
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
