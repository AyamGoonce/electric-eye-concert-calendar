(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.fb9a4e95f41b506f.js","sha256":"fb9a4e95f41b506fd90fb24c97cc61af57510ef8bee799074eedc628ea029dc1","count":244});
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
