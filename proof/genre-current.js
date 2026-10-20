(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6e7ca916af0814dc.js","sha256":"6e7ca916af0814dcb41a3d90e4bfc5313b8a83bfd04e3b4534fce835b26c704c","count":244});
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
