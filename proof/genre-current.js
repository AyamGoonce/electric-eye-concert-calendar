(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.869d29db6bfe02c2.js","sha256":"869d29db6bfe02c229e8b545d870969e6b9398ee0545a637ba11977f8a0e1407","count":244});
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
