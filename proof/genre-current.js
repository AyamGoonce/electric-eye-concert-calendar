(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c4ddd35da1a0b13c.js","sha256":"c4ddd35da1a0b13c0fd2c69f40883bc425dfc572da43ac9ac24e0eedb4dc1933","count":244});
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
