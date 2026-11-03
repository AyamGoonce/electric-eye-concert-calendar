(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8dd05ab26ca26b4b.js","sha256":"8dd05ab26ca26b4b8356ba2f0a00fe92fd42eefaabef85f4ee0979b0f9a83715","count":244});
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
