(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e7ad024d6ee7b003.js","sha256":"e7ad024d6ee7b003afd8c15903d3e7881b7dc5d9a1c4952935f0101fd5b0f468","count":2068,"publishedAt":"2026-09-27T21:25:04Z","state":"calendar-state.json","stateSha256":"9dece9a1a3e4efa8be376cfde028d179a5bdd67df6df5d1ad11f70a592f9a146","sourceState":"calendar-source-state.json","sourceStateSha256":"ee4251672946b95dcaea5f0c3efd44ad74efb4cf497ce5506215fd140a9d126c"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
