(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f5e28b97274e6de5.js","sha256":"f5e28b97274e6de53299ee3638c64339cba9d77d49e565f544f61f579f59a98c","count":244});
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
